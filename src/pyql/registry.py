"""
Adapter registry for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Dict, List, Optional, Type
from .core import DataAdapter, OutputSerializer


class AdapterRegistry:
    """Registry for data adapters and output serializers."""
    
    def __init__(self):
        self._data_adapters: List[Type[DataAdapter]] = []
        self._output_serializers: List[Type[OutputSerializer]] = []
    
    def register_data_adapter(self, adapter: Type[DataAdapter]):
        """Register a data adapter."""
        self._data_adapters.append(adapter)
        return adapter
    
    def register_output_serializer(self, serializer: Type[OutputSerializer]):
        """Register an output serializer."""
        self._output_serializers.append(serializer)
        return serializer
    
    def get_data_adapter(self, data: Any) -> Optional[DataAdapter]:
        """Find an appropriate data adapter for the given data."""
        for adapter_cls in self._data_adapters:
            try:
                adapter = adapter_cls()
                if adapter.can_handle(data):
                    return adapter
            except Exception:
                continue
        return None
    
    def get_output_serializer(self, format_name: str) -> Optional[OutputSerializer]:
        """Find an appropriate output serializer for the given format."""
        for serializer_cls in self._output_serializers:
            try:
                serializer = serializer_cls()
                if serializer.can_serialize(format_name):
                    return serializer
            except Exception:
                continue
        return None


# Global registry instance
registry = AdapterRegistry()