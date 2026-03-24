"Defines the data ingestion notions from various sources."

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from attrs import define
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from exceptions.data_source_exceptions import UnknownDataSource
from helpers.spreadsheet_encoder.chain_of_spreadsheet import (
    identify_table,
    generate_response,
    table_split_qa,
    _find_relevant_sheet,
    _calculate_token_size,
    _predict_header,
)
from helpers.spreadsheet_encoder.Spreadsheet_LLM_Encoder import spreadsheet_llm_encode
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Credentials classes
@dataclass
class _Credentials:
    """Common interface for credentials."""
    username: str
    password: str


# Data storage classes
@dataclass
class _ConnectionConfig:
    sourceType: str
    credentials: _Credentials     # recieves any class instance that inherit from `_Credentials`
    options: dict = field(default_factory=dict)


# Abstract classes
class DataSource(ABC):
    """Common interface for any data source."""
    
    @abstractmethod
    def connect(self, config: _ConnectionConfig) -> None:
        """Initializes a connection for data fetching."""
        ...
    @abstractmethod
    def showDataStructure(self) -> None:
        """Exposes how data is arraged in the source."""
        ...
    @abstractmethod
    def fetch(self) -> None:
        """Fetches specific data or information from source."""
        ...
    @abstractmethod
    def disconnect(self) -> None:
        """Closes connection."""
        ...
        
    # Context managers for safe resource consumption
    def __enter__(self): self.connect(); return self
    def __exit__(self, *_): self.disconnect()
    

# Distinc data sources implementations   
class ExcelFile(DataSource):
    def __init__(self, path: str, tokenLimit: int = 4096):
        self._path = path
        self._tokenLimit = tokenLimit
        self._encoding = Optional[dict] = None
    
    def connect(self, config=None) -> None:
        """Encodes the spreadsheet with SheetCompressor on connect."""
        self._encoding = spreadsheet_llm_encode(self._path)
        if not self._encoding:
            raise ConnectionError(f"Failed to encode spreadsheet: {self._path}")
        logger.info(f"[ExcelFile] Connected and encoded: {self._path}")

    def disconnect(self) -> None:
        self._encoding = None
        logger.info(f"[ExcelFile] Disconnected: {self._path}")

    def fetch(self) -> Any:
        """Returns the raw encoding for downstream consumers."""
        return self._encoding

    def showDataStructure(self) -> Dict:
        """
        Exposes how data is arranged in the Excel source using the
        `Chain-of-Spreadsheet (CoS)` pipeline from `SpreadsheetLLM`.

        Returns a structured summary dict with:
        - encoding: full SheetCompressor output (compressed representation)
        - sheets: per-sheet metadata (tables detected, header ranges, token sizes)
        - query_fn: a callable that performs CoS two-stage QA over this file

        The returned dict is designed to be injected into any LLM system prompt
        so the model can reason about the spreadsheet before chart generation.
        """
        if not self._encoding:
            raise RuntimeError(
                "ExcelFile must be connected before calling showDataStructure(). "
                "Use 'with ExcelFile(...) as f:' or call .connect() first."
            )

        structure: Dict = {
            "source": self._path,
            "sheets": {},
            "encoding": self._encoding,
            "query_fn": self._cos_query,   # expose CoS QA as a first-class callable
        }

        for sheet_name, sheet_data in self._encoding.get("sheets", {}).items():
            structural_probe = (
                "List every distinct table present in this sheet "
                "and return each one's range."
            )
            detected_range = identify_table(self._encoding, structural_probe)

            # ── Estimate token budget consumed by this sheet ───────────────────
            token_estimate = _calculate_token_size(sheet_data)

            # ── Predict header for each detected table ─────────────────────────
            header_data, header_range = (
                _predict_header(sheet_data, detected_range)
                if detected_range
                else ({}, None)
            )

            structure["sheets"][sheet_name] = {
                "compressed_data": sheet_data,
                "detected_table_range": detected_range,   # e.g. "A1:F9"
                "header_range": header_range,             # e.g. "1:1"
                "header_data": header_data,
                "token_estimate": token_estimate,
                "needs_split": token_estimate > self._token_limit,
            }

        return structure
    
    # ── Private helper: two-stage CoS QA ──────────────────────────────────────────

    def _cos_query(self, query: str) -> str:
        """
        Runs the full Chain-of-Spreadsheet two-stage pipeline for a given query.

        Stage 1 --> Table Identification:
            Feed the *compressed* encoding + query to the LLM.
            The model returns the cell range of the most relevant table.

        Stage 2 --> Response Generation:
            Feed the *uncompressed* (or minimally compressed) table + query.
            The model returns the cell address (or formula) that answers the query.
            If the table exceeds self._token_limit, Table Split QA is applied.

        Parameters
        ----------
        query : str
            Natural-language question about the spreadsheet data
            (e.g. "What were total sales in Q3?").

        Returns
        -------
        str
            Cell address, formula, or aggregated answer from the LLM.
        """
        if not self._encoding:
            raise RuntimeError("Not connected. Call connect() before querying.")

        # ── Stage 1: locate the relevant table ────────────────────────────────
        table_range = identify_table(self._encoding, query)
        if not table_range:
            return (
                "Could not identify a relevant table for the given query. "
                "Verify that the spreadsheet contains data related to the question."
            )

        logger.info(f"[CoS Stage 1] Identified table range: {table_range}")

        # ── Resolve which sheet owns that range ───────────────────────────────
        # identify_table works on the full encoding; we need to pick the sheet
        # whose compressed data the LLM actually used.  We re-run _find_relevant_sheet
        # (already imported from chain_of_spreadsheet) for consistency.
        sheet_name = _find_relevant_sheet(self._encoding, query)
        if not sheet_name:
            return "Could not resolve the sheet containing the identified table."

        sheet_data = self._encoding["sheets"][sheet_name]
        token_size = _calculate_token_size(sheet_data)

        logger.info(
            f"[CoS Stage 2] Sheet '{sheet_name}' | "
            f"tokens ≈ {token_size} | limit = {self._token_limit}"
        )

        # ── Stage 2: generate response (with split if needed) ─────────────────
        if token_size > self._token_limit:
            logger.info("[CoS Stage 2] Table exceeds token limit -> Table Split QA")
            answer = table_split_qa(
                sheet_data=sheet_data,
                table_range=table_range,
                query=query,
                token_limit=self._token_limit,
            )
        else:
            answer = generate_response(sheet_data, query)
        logger.info(f"[CoS Stage 2] Raw LLM answer: {answer}")
        return answer


# Main class 
class DataSourceFactory:
    """Manages data sources."""
    _registry: dict[str, type[DataSource]] = {
        ...
    }
    
    @classmethod
    def registerNewSource(cls, name: str, kclass: type[DataSource]) -> None:
        """Registers a new data source."""
        cls._registry[name] = kclass
        
    @classmethod
    def createSourceInstance(cls, config:_ConnectionConfig) -> DataSource:
        """Creates a new source instance for working with."""
        kclass = cls._registry.get(config.sourceType)
        if not kclass:
            availableSources = list(cls._registry.keys())
            raise UnknownDataSource(f"Data source not available: '{config.sourceType}'."
                             f"Supported sources: '{availableSources}'")
        return kclass()
    