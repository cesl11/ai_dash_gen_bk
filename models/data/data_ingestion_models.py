"Defines the data ingestion notions from various sources."
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

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
    def fetch(self) -> None:
        """Extracts data."""
        ...
    @abstractmethod
    def disconnect(self) -> None:
        """Closes connection."""
        ...
        
    # Context managers for safe resource consumption
    def __enter__(self): self.connect(); return self
    def __exit__(self, *_): self.disconnect()
    

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
            raise ValueError(f"Unknown data source: '{config.sourceType}'."
                             f"Supported sources: '{availableSources}'")
        return kclass()
    