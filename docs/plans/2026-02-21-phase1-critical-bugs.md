# Phase 1: Critical Bugs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 9 critical runtime bugs that prevent the codebase from functioning, achieving 100% test pass rate.

**Architecture:** Each bug is an independent fix with no inter-dependencies. Fixes range from syntax corrections to logic fixes. All can be done in parallel. After each bug is fixed, run relevant tests to verify.

**Tech Stack:** Python 3.8+, pytest, LangChain, javalang parser

**Estimated Total Time:** 4-5 hours

---

## Task 1: Fix state_diff.py Syntax Error

**Files:**
- Modify: `src/utils/state_diff.py:56`

**Step 1: Read the file to see the error**

Run: `head -60 src/utils/state_diff.py | tail -10`

Expected: See the syntax error around line 56 (missing comma)

**Step 2: Apply the fix**

File: `src/utils/state_diff.py` around line 56

```python
# BEFORE
summary = {
    "added": 0,
    "removed": 0,
    "modified": 0         # ← missing comma
    "classes_changed": 0,
}

# AFTER
summary = {
    "added": 0,
    "removed": 0,
    "modified": 0,        # ← add comma here
    "classes_changed": 0,
}
```

**Step 3: Verify the import works**

Run: `python -c "from src.utils.state_diff import *; print('✓ Import successful')"`

Expected: `✓ Import successful`

**Step 4: Commit**

```bash
git add src/utils/state_diff.py
git commit -m "fix: add missing comma in state_diff.py:56 summary dict"
```

---

## Task 2: Remove java_tools.py Dead Code Block

**Files:**
- Modify: `src/tools/java_tools.py:265-324`

**Step 1: Verify the dead code exists**

Run: `sed -n '240,270p' src/tools/java_tools.py`

Expected: See the return statement around line 245, followed by unreachable code starting line 265

**Step 2: Identify the exact lines to delete**

The dead code is lines 265-324. The code before it (lines 240-264) ends with `except Exception as e: return {...}`

**Step 3: Delete the unreachable block**

Remove lines 265-324 entirely. The file should go from line 264 (end of except block) to line 326 (next code after dead block).

Verify with: `sed -n '264,266p' src/tools/java_tools.py` - should show line 264 is last line of code, line 266 is end of file or continuation

**Step 4: Run tests to verify no breakage**

Run: `python -m pytest tests/test_tools.py::TestJavaTools -v --tb=short`

Expected: No new failures introduced

**Step 5: Commit**

```bash
git add src/tools/java_tools.py
git commit -m "fix: remove unreachable dead code block in java_tools.py:265-324"
```

---

## Task 3: Add @dataclass to CodeSmell and SecurityIssue

**Files:**
- Modify: `src/tools/code_quality_tools.py:1-30`

**Step 1: View the current classes**

Run: `sed -n '1,30p' src/tools/code_quality_tools.py`

Expected: See CodeSmell and SecurityIssue class definitions without @dataclass

**Step 2: Add dataclass import**

File: `src/tools/code_quality_tools.py` line 1-5

```python
# BEFORE
import javalang

# AFTER
from dataclasses import dataclass
import javalang
```

**Step 3: Add @dataclass decorator to CodeSmell**

File: `src/tools/code_quality_tools.py` around line 10

```python
# BEFORE
class CodeSmell:
    name: str

# AFTER
@dataclass
class CodeSmell:
    name: str
```

**Step 4: Add @dataclass decorator to SecurityIssue**

File: `src/tools/code_quality_tools.py` around line 17

```python
# BEFORE
class SecurityIssue:
    issue_type: str

# AFTER
@dataclass
class SecurityIssue:
    issue_type: str
```

**Step 5: Test that classes can be instantiated**

Run: `python -c "from src.tools.code_quality_tools import CodeSmell, SecurityIssue; cs = CodeSmell('test', 'desc', 1, 'high'); print(f'✓ CodeSmell: {cs.name}'); si = SecurityIssue('bug', 'desc', 2, 'high'); print(f'✓ SecurityIssue: {si.issue_type}')"`

Expected: Both success messages printed

**Step 6: Commit**

```bash
git add src/tools/code_quality_tools.py
git commit -m "fix: add @dataclass decorator to CodeSmell and SecurityIssue"
```

---

## Task 4: Add Missing javalang Import to analyze_project.py

**Files:**
- Modify: `src/agents/analyze_project.py:1-10`

**Step 1: Check current imports**

Run: `head -10 src/agents/analyze_project.py`

Expected: See imports but no `import javalang`

**Step 2: Add javalang import**

File: `src/agents/analyze_project.py` after line 5

```python
# BEFORE
import os
import json
from pathlib import Path
from ..utils.java_parser import parse_java_file, extract_imports, extract_dependencies

# AFTER
import os
import json
import javalang
from pathlib import Path
from ..utils.java_parser import parse_java_file, extract_imports, extract_dependencies
```

**Step 3: Verify the import resolves**

Run: `python -c "from src.agents.analyze_project import AnalyzeProjectAgent; print('✓ Import successful')"`

Expected: `✓ Import successful`

**Step 4: Commit**

```bash
git add src/agents/analyze_project.py
git commit -m "fix: add missing javalang import to analyze_project.py"
```

---

## Task 5: Fix workflow.py Test Results Data Loss Bug

**Files:**
- Modify: `src/graphs/workflow.py:78-102`

**Step 1: View the buggy code**

Run: `sed -n '78,102p' src/graphs/workflow.py`

Expected: See loop that overwrites `result` each iteration, then only captures last result

**Step 2: Identify the issue**

The code is:
```python
for test_class in test_classes:
    ...
    result = await validate_test_agent.process(test_state)

test_results = result.get("test_results", {})  # Only LAST result
```

**Step 3: Fix by accumulating results**

File: `src/graphs/workflow.py` around line 78-102

```python
# BEFORE
for test_class in test_classes:
    ...
    result = await validate_test_agent.process(test_state)
    ...

test_results = result.get("test_results", {})

# AFTER
all_test_results = {}
for test_class in test_classes:
    ...
    result = await validate_test_agent.process(test_state)
    all_test_results.update(result.get("test_results", {}))
    ...

test_results = all_test_results
```

**Step 4: Run tests to verify fix**

Run: `python -m pytest tests/test_integration.py -v -k validate --tb=short`

Expected: Test validation tests pass

**Step 5: Commit**

```bash
git add src/graphs/workflow.py
git commit -m "fix: accumulate test results across loop iterations in workflow.py"
```

---

## Task 6: Fix concurrent.py Async Tasks in ThreadPoolExecutor

**Files:**
- Modify: `src/utils/concurrent.py:30-100`

**Step 1: View the buggy code**

Run: `sed -n '25,100p' src/utils/concurrent.py | grep -A 20 'ThreadPoolExecutor\|async def run'`

Expected: See ThreadPoolExecutor being used with coroutines

**Step 2: Identify the problem**

Lines show: `executor = ThreadPoolExecutor(max_workers=max_workers)` being used with async tasks

**Step 3: Replace ThreadPoolExecutor with asyncio tasks**

File: `src/utils/concurrent.py` - find `run_concurrent_tasks` function

```python
# BEFORE
async def run_concurrent_tasks(async_tasks, max_workers=5):
    executor = ThreadPoolExecutor(max_workers=max_workers)
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(executor, task) for task in async_tasks]
    return await asyncio.gather(*futures)

# AFTER
async def run_concurrent_tasks(async_tasks, max_workers=5):
    """Run async tasks concurrently with max_workers limit"""
    semaphore = asyncio.Semaphore(max_workers)

    async def bounded_task(task):
        async with semaphore:
            return await task()

    tasks = [bounded_task(task) for task in async_tasks]
    return await asyncio.gather(*tasks)
```

**Step 4: Also fix line 132 issue (process_single_file)**

Find the similar pattern around line 130-135 and apply same fix

**Step 5: Run tests**

Run: `python -m pytest tests/ -v -k concurrent --tb=short`

Expected: Tests pass

**Step 6: Commit**

```bash
git add src/utils/concurrent.py
git commit -m "fix: use asyncio tasks instead of ThreadPoolExecutor for async operations"
```

---

## Task 7: Fix maven_dependency_tools.py Dict Access

**Files:**
- Modify: `src/tools/maven_dependency_tools.py:56-57`

**Step 1: View the buggy code**

Run: `sed -n '50,65p' src/tools/maven_dependency_tools.py`

Expected: See `result.stdout` and `result.stderr` being accessed as object attributes

**Step 2: Identify the issue**

Code shows: `result = _run_maven_command(...)` returning a dict, but then `result.stdout` instead of `result["stdout"]`

**Step 3: Fix the dict access**

File: `src/tools/maven_dependency_tools.py` around lines 56-57

```python
# BEFORE
result = _run_maven_command(project_path, "dependency:resolve")
parse_output(result.stdout, graph)

# AFTER
result = _run_maven_command(project_path, "dependency:resolve")
parse_output(result["stdout"], graph)
```

Also fix any other `result.stderr` to `result["stderr"]`

**Step 4: Run tests**

Run: `python -m pytest tests/test_tools.py::TestMavenTools -v --tb=short`

Expected: Tests pass

**Step 5: Commit**

```bash
git add src/tools/maven_dependency_tools.py
git commit -m "fix: access maven_dependency_tools result dict with bracket notation"
```

---

## Task 8: Fix access_control.py reset() Type Mismatch

**Files:**
- Modify: `src/utils/access_control.py:296-303`

**Step 1: View the buggy code**

Run: `sed -n '290,310p' src/utils/access_control.py`

Expected: See `_allowed_paths = []` and `_restricted_paths = []` in reset() method

**Step 2: Identify the issue**

These fields are initialized as `set()` but reset() sets them to `[]` (list), causing AttributeError when `.add()` is called later

**Step 3: Fix the reset method**

File: `src/utils/access_control.py` in `reset()` method

```python
# BEFORE
def reset(self) -> None:
    with self._lock:
        self._project_root = None
        self._allowed_paths = []
        self._restricted_paths = []
        # ... rest

# AFTER
def reset(self) -> None:
    with self._lock:
        self._project_root = None
        self._allowed_paths = set()
        self._restricted_paths = set()
        # ... rest
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_tools.py -v -k access --tb=short`

Expected: Tests pass

**Step 5: Commit**

```bash
git add src/utils/access_control.py
git commit -m "fix: reset() should initialize sets not lists in access_control.py"
```

---

## Task 9: Fix state_manager.py JSON Serialization

**Files:**
- Modify: `src/utils/state_manager.py:140-160`

**Step 1: View the buggy code**

Run: `sed -n '140,160p' src/utils/state_manager.py`

Expected: See `json.dumps(state_data, ...)` where state_data contains BaseMessage objects

**Step 2: Understand the issue**

`ProjectState` has `messages: list[BaseMessage]`. LangChain BaseMessage objects are not JSON serializable.

**Step 3: Create helper to make state serializable**

File: `src/utils/state_manager.py` - add function before `_create_snapshot`

```python
def _make_serializable(state: dict) -> dict:
    """Convert non-serializable objects in state to serializable form."""
    state_copy = copy.deepcopy(state)
    if "messages" in state_copy:
        state_copy["messages"] = [
            msg.model_dump() if hasattr(msg, 'model_dump') else str(msg)
            for msg in state_copy.get("messages", [])
        ]
    return state_copy
```

**Step 4: Update _create_snapshot to use helper**

File: `src/utils/state_manager.py` in `_create_snapshot` method

```python
# BEFORE
state_data = copy.deepcopy(self._current_state)
state_str = json.dumps(state_data, sort_keys=True)

# AFTER
state_data = _make_serializable(self._current_state)
state_str = json.dumps(state_data, sort_keys=True)
```

**Step 5: Test serialization works**

Run: `python -c "from src.utils.state_manager import StateManager; from src.states.project import ProjectState; print('✓ Serialization test OK')"`

Expected: No errors, success message

**Step 6: Commit**

```bash
git add src/utils/state_manager.py
git commit -m "fix: handle non-serializable BaseMessage objects in state_manager JSON serialization"
```

---

## Verification Steps (After All Tasks Complete)

**Step 1: Run all tests**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: 100% pass rate (or near 100%)

**Step 2: Check for import errors**

```bash
python -c "
from src.utils.state_diff import *
from src.tools.java_tools import *
from src.tools.code_quality_tools import *
from src.agents.analyze_project import *
from src.graphs.workflow import *
from src.utils.concurrent import *
from src.tools.maven_dependency_tools import *
from src.utils.access_control import *
from src.utils.state_manager import *
print('✓ All modules import successfully')
"
```

Expected: Success message with no errors

**Step 3: Run specific integration test**

```bash
python -m pytest tests/test_integration.py -v
```

Expected: All integration tests pass

**Step 4: Final commit**

```bash
git log --oneline -9
```

Expected: See 9 commits for each bug fix

---

## Summary

**Total Tasks:** 9 independent bug fixes
**Estimated Time:** 4-5 hours
**Test Coverage After:** ~100% (up from 98.2%)
**Commits:** 9 (one per fix)

**Execution Path:** Each task is independent and can be done in any order or in parallel.

---

## Execution Instructions

This plan is ready to execute using one of two approaches:

**Option 1: Subagent-Driven (Recommended for this session)**
- Use superpowers:subagent-driven-development
- Fresh subagent per task (or 2-3 tasks per subagent)
- Review between batches
- Faster iteration, more control

**Option 2: Parallel Session**
- Open new session in worktree
- Use superpowers:executing-plans
- Batch execution with checkpoints
- Better for background work

Which approach would you like to use?
