from typing import Any, Callable, Dict, Optional, Type
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    """Definition of a tool in the registry."""
    
    name: str
    func: Callable
    description: str
    is_async: bool = False


class ToolRegistry:
    """
    Central registry for all tools with dependency injection support.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._mocks: Dict[str, Any] = {}
    
    def register(self, name: str, func: Callable, description: str = "", is_async: bool = False) -> None:
        """
        Register a tool in the registry.
        
        Args:
            name: Unique name for the tool
            func: Tool function to register
            description: Optional description of the tool
            is_async: Whether the tool is async
        """
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        self._tools[name] = ToolDefinition(
            name=name,
            func=func,
            description=description,
            is_async=is_async
        )
    
    def register_module(self, module_path: str) -> None:
        """
        Register all tools from a module.
        
        Args:
            module_path: Python module path (e.g., "src.tools.file_tools")
        """
        import importlib
        import sys
        
        from pathlib import Path
        
        module_name = Path(module_path).stem
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, '__doc__'):
                    self.register(attr_name, attr, getattr(attr, '__doc__', ''))
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
        
        Returns:
            Tool function or None if not found
        """
        if name in self._mocks:
            return self._mocks[name]
        
        tool_def = self._tools.get(name)
        return tool_def.func if tool_def else None
    
    def mock_tool(self, name: str, mock: Any) -> None:
        """
        Mock a tool for testing purposes.
        
        Args:
            name: Name of the tool to mock
            mock: Mock object to use instead
        """
        self._mocks[name] = mock
    
    def unmock_tool(self, name: str) -> None:
        """
        Remove mock for a tool.
        
        Args:
            name: Name of the tool to unmock
        """
        if name in self._mocks:
            del self._mocks[name]
    
    def clear_mocks(self) -> None:
        """Clear all tool mocks."""
        self._mocks.clear()
    
    def list_tools(self) -> list[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[ToolDefinition]:
        """
        Get detailed information about a tool.
        
        Args:
            name: Name of the tool
        
        Returns:
            ToolDefinition or None if not found
        """
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, ToolDefinition]:
        """
        Get all registered tools.
        
        Returns:
            Dictionary mapping tool names to their definitions
        """
        return self._tools.copy()


_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry.
    
    Returns:
        ToolRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = ToolRegistry()
    
    return _global_registry


def get_tool(name: str) -> Optional[Callable]:
    """
    Convenience function to get a tool from the global registry.
    
    Args:
        name: Name of the tool to retrieve
    
    Returns:
        Tool function or None if not found
    """
    return get_registry().get_tool(name)


def register_tool(name: str, func: Callable, description: str = "", is_async: bool = False) -> None:
    """
    Convenience function to register a tool.
    
    Args:
        name: Unique name for the tool
        func: Tool function to register
        description: Optional description of the tool
        is_async: Whether the tool is async
    """
    get_registry().register(name, func, description, is_async)
