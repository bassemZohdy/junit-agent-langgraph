# Unified DTO Pattern: JavaClassState as Common Model

**Status**: ✅ Implemented in Phase 1
**Key File**: `src/tools/java_tools.py`
**Pattern**: TypedDict as DTO across all layers

---

## The Pattern: Why JavaClassState?

Instead of each tool returning different formats:
```python
# ❌ OLD: Inconsistent formats
get_java_classes() → "Class: Foo\nInterface: Bar"  # String
get_java_methods() → "  public void bar()"         # String
extract_classes_from_tree() → {"name": "Foo", ...} # Dict

# ✅ NEW: Unified format
create_java_class_state() → JavaClassState         # DTO
extract_all_classes_as_states() → str (uses JavaClassState internally)
extract_classes_from_tree() → List[JavaClassState] # DTO
```

---

## What is JavaClassState?

**Definition**: A `TypedDict` that represents complete information about a Java class.

```python
class JavaClassState(TypedDict):
    name: str                           # Class name
    file_path: str                      # Source file path
    package: Optional[str]              # Package name
    content: Optional[str]              # Full source code
    type: str                           # "class", "interface", or "enum"
    modifiers: list[str]                # ["public", "final", ...]
    extends: Optional[str]              # Parent class name
    implements: list[str]               # Interface names
    annotations: list[AnnotationState]  # Class annotations
    fields: list[FieldState]            # Class fields
    methods: list[MethodState]          # Class methods
    imports: list[ImportState]          # File imports
    inner_classes: list["JavaClassState"]  # Nested classes
    status: str                         # "analyzed" or "error"
    errors: list[str]                   # Error messages if status="error"
    line_number: Optional[int]          # Line where class is defined
```

---

## Why Use DTOs?

### 1. **Consistency Across Layers**
```python
# Agents, Tools, and other components all understand JavaClassState
class AnalyzeProjectAgent:
    async def _analyze_java_file(self, file_path: str, ...):
        tree = parse_java_file(content)
        classes = extract_classes_from_tree(tree, file_path)  # → List[JavaClassState]

        for cls in classes:  # cls is JavaClassState
            print(f"Class: {cls['name']}")
            for method in cls['methods']:  # methods is List[MethodState]
                print(f"  Method: {method['name']}")
```

### 2. **Type Safety**
```python
# IDEs provide autocomplete
class_state: JavaClassState = {...}
class_state['name']      # ✓ IDE knows this exists
class_state['nonexistent']  # ✗ IDE warns: Invalid key
```

### 3. **Easy Serialization**
```python
import json

# Convert to JSON for storage/transmission
json_str = json.dumps(class_state, default=str)

# Or convert back from JSON
loaded_state: JavaClassState = json.loads(json_str)
```

### 4. **Clear Data Contracts**
```python
# Function signature makes data flow explicit
def analyze_class(cls: JavaClassState) -> ClassAnalysis:
    """
    Takes a complete JavaClassState
    Returns ClassAnalysis with findings
    """
    # Type hints make it clear what data is available
    method_count = len(cls['methods'])
    field_count = len(cls['fields'])
```

---

## Real-World Usage Examples

### Example 1: Agent Using DTO
```python
# src/agents/analyze_project.py
from ..tools.java_tools import extract_classes_from_tree

class AnalyzeProjectAgent(BaseAgent):
    async def _analyze_java_file(self, file_path: str):
        tree = parse_java_file(content)

        # Get structured data via DTO
        classes: List[JavaClassState] = extract_classes_from_tree(tree, file_path)

        for class_state in classes:
            # Type-safe access to all class information
            print(f"Analyzing: {class_state['name']}")

            # Methods are typed as List[MethodState]
            for method in class_state['methods']:
                print(f"  Method: {method['name']}()")

            # Fields are typed as List[FieldState]
            for field in class_state['fields']:
                print(f"  Field: {field['name']}: {field['type']}")
```

### Example 2: Tool Returning DTO
```python
# src/tools/java_tools.py
@tool
def create_java_class_state(source_file: str) -> JavaClassState:
    """Returns complete class information as structured DTO."""
    tree = _parse_java_file(source_file)
    classes = _extract_class_details_from_tree(source_file, tree)
    return classes[0] if classes else error_state
```

### Example 3: LLM Integration with DTO
```python
# Using DTO with Claude
import json

class_state: JavaClassState = create_java_class_state("User.java")

# Convert DTO to JSON for Claude
json_data = json.dumps(class_state, default=str)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": f"""
        Analyze this Java class and suggest improvements:

        {json_data}
        """
    }]
)
```

---

## Breaking Down JavaClassState Components

### FieldState DTO
```python
class FieldState(TypedDict):
    name: str                      # Field name
    type: str                      # Data type (String, int, etc.)
    modifiers: list[str]           # ["public", "static", "final"]
    is_static: bool                # Convenience flag
    is_final: bool                 # Convenience flag
    default_value: Optional[str]   # Initial value if any
    annotations: list[AnnotationState]  # Field annotations
    line_number: Optional[int]     # Where field is defined
```

### MethodState DTO
```python
class MethodState(TypedDict):
    name: str                      # Method name
    return_type: str               # Return type
    parameters: list[dict[str, str]]  # Parameters: [{"name": "x", "type": "int"}]
    modifiers: list[str]           # ["public", "static", "abstract"]
    annotations: list[AnnotationState]  # Method annotations
    throws: list[str]              # Exception types
    body: Optional[str]            # Method body code
    is_abstract: bool              # Convenience flag
    line_number: Optional[int]     # Where method is defined
```

### AnnotationState DTO
```python
class AnnotationState(TypedDict):
    name: str                      # Annotation name
    elements: dict[str, str]       # @Annotation(key="value", ...)
    target: Optional[str]          # "class", "method", "field"
    line_number: Optional[int]     # Where annotation is defined
```

---

## How Extraction Works with DTOs

### Flow Diagram
```
┌─────────────────────────────────────────────┐
│ Java Source File (User.java)                │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ javalang.parse() → AST Tree                 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ _extract_class_details_from_tree()          │
│   ├─ Iterate through tree                   │
│   ├─ For each ClassDeclaration:             │
│   │   ├─ Extract fields → FieldState[]      │
│   │   ├─ Extract methods → MethodState[]    │
│   │   ├─ Extract annotations → AnnotationState[]
│   │   └─ Combine into JavaClassState        │
│   └─ Return List[JavaClassState]            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ JavaClassState Objects                      │
│ {                                           │
│   "name": "User",                           │
│   "type": "class",                          │
│   "fields": [...],                          │
│   "methods": [...],                         │
│   ...                                       │
│ }                                           │
└─────────────────────────────────────────────┘
```

---

## Adding New Information to DTOs

If you need to add new information to classes:

### Step 1: Update the DTO Definition
```python
class JavaClassState(TypedDict):
    # ... existing fields ...
    complexity_score: Optional[int]  # NEW: McCabe complexity
    deprecated: bool                 # NEW: @Deprecated flag
```

### Step 2: Update the Extraction Logic
```python
def _extract_class_details_from_tree(source_file, tree):
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            # ... existing extraction ...

            # NEW: Calculate complexity
            complexity_score = calculate_complexity(node)

            # NEW: Check for @Deprecated
            deprecated = any(
                ann.name == "Deprecated"
                for ann in node.annotations
            )

            class_state = {
                # ... existing fields ...
                "complexity_score": complexity_score,
                "deprecated": deprecated,
            }
```

### Step 3: All Tools Automatically Benefit
- ✓ `create_java_class_state()` returns new fields
- ✓ `extract_all_classes_as_states()` includes new fields
- ✓ Agents automatically see new data in JavaClassState
- ✓ IDEs provide autocomplete for new fields

---

## Benefits for Different Roles

### For Developers
- ✓ Type hints enable IDE autocomplete
- ✓ Clear data structure documentation
- ✓ Easy to understand what data is available
- ✓ Compile-time checking with static analysis

### For Agents/LLMs
- ✓ Structured JSON format
- ✓ Consistent across all class extractions
- ✓ Easy to parse and understand
- ✓ Complete information in one place

### For Tests
- ✓ Easy to create test fixtures
- ✓ Simple to validate structure
- ✓ Type checkers verify test data

### For Future Maintenance
- ✓ Single source of truth
- ✓ Changes propagate everywhere
- ✓ No inconsistencies to debug
- ✓ Clear dependencies between components

---

## Comparison: Before vs. After

### Before (String-Based)
```python
# Tool returns string
result = get_java_classes("User.java")
# "Class: User (extends BaseEntity)\nInterface: Comparable"

# Agent has to parse it
if "Class: " in result:
    # Parse string manually
    class_name = result.split(":")[1].strip()
    # Error-prone, fragile
```

### After (DTO-Based)
```python
# Tool returns structured data
classes = extract_all_classes_as_states("User.java")

# Agent uses typed data
for cls in classes:  # cls is JavaClassState
    print(cls['name'])  # Direct, type-safe access
    print(cls['extends'])  # IDE knows this field exists
```

---

## Migration Guide: Applying to Other Extractors

This pattern can be applied to:

### 1. Import Extraction
```python
class ImportState(TypedDict):  # ✓ Already exists
    name: str
    is_static: bool
    is_wildcard: bool
    line_number: Optional[int]
```

### 2. Annotation Extraction
```python
class AnnotationState(TypedDict):  # ✓ Already exists
    name: str
    elements: dict[str, str]
    target: Optional[str]
    line_number: Optional[int]
```

### 3. Dependency Extraction
```python
class DependencyState(TypedDict):
    group_id: str
    artifact_id: str
    version: str
    scope: str
    transitive: List["DependencyState"]
```

---

## Summary: DTO Pattern Principles

1. **Create a TypedDict** for your data structure
2. **Centralize extraction** logic that populates it
3. **Use consistently** across all tools/agents
4. **Extend by updating** the TypedDict
5. **Benefit everywhere** automatically

Result:
- ✅ Type-safe data passing
- ✅ Single source of truth
- ✅ Consistent interfaces
- ✅ Easy maintenance
- ✅ Better LLM integration

---

**Created**: 2026-02-21
**Pattern**: Applied to JavaClassState, MethodState, FieldState, AnnotationState, ImportState
**Next**: Apply same pattern to DependencyState, TestState, ValidationState
