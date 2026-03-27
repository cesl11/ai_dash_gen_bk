"Defines the data ingestion notions from various sources."

import os
import sys
# Add project root to sys.path for aux imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal
from aux.validators.args_validation.decorators import validate
from aux.validators.files_validation.functions import validatePath
from exceptions.data.data_source_exceptions import UnknownDataSource

from e2b_code_interpreter import Sandbox
from dotenv import load_dotenv

# Set up env variables
load_dotenv()

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


# Common interfaces classes
class DataSource(ABC):
    """Common interface for any data source."""    
    @abstractmethod
    def fetch(self) -> Any:
        """Fetches specific data or information from source."""
        ...

class Connectable(ABC):
    """Common interface for any data source that needs to be connected (databases, APIs...)."""
    @abstractmethod
    def connect(self, config: _ConnectionConfig) -> Any:
        """Opens a new connection for any connectable data source."""
        ...
    @abstractmethod
    def disconnect(self) -> Any: 
        """Closes the opened connection."""
        ...
        
    # Context managers for safe resource consumption 
    def __enter__(self): self.connect(); return self 
    def __exit__(self, *_): self.disconnect()
    
    

# Distinc data sources implementations   
class ExcelFile(DataSource):
    @validate
    def __init__(self, 
                filepath: str, 
                sandbox_env: Literal['E2B', 'LOCAL'] = 'LOCAL'):
        try:
            validatePath(filepath)
        except FileNotFoundError:
            raise
        except TypeError:
            raise
        except ValueError:
            raise
        self.filepath = filepath 
        self._sandbox_env = sandbox_env
        
    # continue here

        


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
 
 
x = ExcelFile('/Users/cesl11/Downloads/shuHOTELES CANCUN 2024 joshua.xlsx', ['opo'])  
print(x) 