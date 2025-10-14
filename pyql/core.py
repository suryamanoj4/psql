"""
Core interfaces for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Dict, List
from pathlib import Path


class DataSource(ABC):
    """Abstract base class for different data sources."""
    
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Return an iterator over records as dictionaries."""
        pass


class DataAdapter(ABC):
    """Abstract base class for data adapters."""
    
    @abstractmethod
    def can_handle(self, data: Any) -> bool:
        """Check if this adapter can handle the given data."""
        pass
    
    @abstractmethod
    def adapt(self, data: Any) -> DataSource:
        """Convert the input data to a DataSource."""
        pass


class OutputSerializer(ABC):
    """Abstract base class for output serializers."""
    
    @abstractmethod
    def can_serialize(self, format_name: str) -> bool:
        """Check if this serializer can handle the given format."""
        pass
    
    @abstractmethod
    def serialize(self, data: Iterator[Dict[str, Any]], format_name: str) -> Any:
        """Serialize the data to the requested format."""
        pass