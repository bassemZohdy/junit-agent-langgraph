"""Formatters for Java class states and related objects."""

from ..states.project import JavaClassState


class JavaClassStateFormatter:
    """Formatter for JavaClassState objects with clean string representation."""

    def __init__(self, class_state: JavaClassState):
        self.class_state = class_state

    def __str__(self) -> str:
        """Format JavaClassState as readable text for display/LLM consumption."""
        lines = [f"Class: {self.class_state['name']}"]
        if self.class_state.get("package"):
            lines.append(f"  Package: {self.class_state['package']}")
        if self.class_state.get("extends"):
            lines.append(f"  Extends: {self.class_state['extends']}")
        if self.class_state.get("implements"):
            lines.append(f"  Implements: {', '.join(self.class_state['implements'])}")
        if self.class_state.get("annotations"):
            ann_names = [a["name"] for a in self.class_state.get("annotations", [])]
            lines.append(f"  Annotations: {', '.join(ann_names)}")
        if self.class_state.get("fields"):
            lines.append(f"  Fields ({len(self.class_state['fields'])}):")
            for field in self.class_state["fields"]:
                modifiers = " ".join(field.get("modifiers", []))
                mod_str = f"{modifiers} " if modifiers else ""
                lines.append(f"    {mod_str}{field['type']} {field['name']}")
        if self.class_state.get("methods"):
            lines.append(f"  Methods ({len(self.class_state['methods'])}):")
            for method in self.class_state["methods"]:
                modifiers = " ".join(method.get("modifiers", []))
                mod_str = f"{modifiers} " if modifiers else ""
                params = ", ".join([f"{p['type']} {p['name']}" for p in method.get("parameters", [])])
                lines.append(f"    {mod_str}{method['return_type']} {method['name']}({params})")
        if self.class_state.get("imports"):
            lines.append(f"  Imports ({len(self.class_state['imports'])}):")
            for imp in self.class_state["imports"][:10]:  # Show first 10
                lines.append(f"    {imp['name']}")
            if len(self.class_state["imports"]) > 10:
                lines.append(f"    ... and {len(self.class_state['imports']) - 10} more")
        return "\n".join(lines)

    def to_string(self) -> str:
        """Alias for __str__ for explicit conversion."""
        return str(self)
