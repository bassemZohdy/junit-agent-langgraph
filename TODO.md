# TODO

This document tracks planned features, improvements, and tasks for the LangGraph + Ollama Java test generation application.

## Priorities

- 🔴 High - Critical functionality or blocking issues
- 🟡 Medium - Important features and improvements
- 🟢 Low - Nice to have features and enhancements

---

## Core Functionality

### 🟢 Low Priority

- [ ] Add code formatting
  - Format Java files according to Google/Oracle style
  - Fix imports (remove unused, organize)
  - Add missing javadoc
  - Optimize imports order

- [ ] Implement template system
  - Create Java class templates
  - Create method templates
  - Create test templates
  - Custom template support

---

## State Management

### 🟡 Medium Priority

- [ ] Add state diffing and comparison
  - Compare two ProjectState objects
  - Generate diff report
  - Highlight changed components
  - Export diff as readable format

- [ ] Implement state persistence options
  - Save state to JSON/YAML files
  - Load state from saved files
  - Compare file system state with saved state
  - Detect drift

### 🟢 Low Priority

- [ ] Add state versioning
  - Track state schema versions
  - Handle state migrations
  - Backward compatibility support
  - Schema validation

---

## User Interface

### 🟡 Medium Priority

- [ ] Add interactive mode
  - Confirm before destructive operations
  - Select from multiple options
  - Interactive file selection
  - Step-by-step workflows

- [ ] Implement command aliases
  - Create shortcuts for common commands
  - User-defined aliases
  - Save/load alias configurations

### 🟢 Low Priority

- [ ] Add web interface
  - Simple Flask/FastAPI frontend
  - Visual project explorer
  - Interactive code editor
  - Real-time state visualization

---

## Testing

### 🔴 High Priority

- [ ] Add integration tests
  - Test complete workflows
  - Test with real Java projects
  - Test error scenarios
  - Test concurrent operations

### 🟡 Medium Priority

- [ ] Add end-to-end tests
  - Test from project analysis to code changes
  - Test Maven build workflows
  - Test multi-file operations
  - Performance benchmarking

- [ ] Add property-based tests
  - Generate random test cases
  - Test edge cases
  - Fuzzing for file operations
  - Contract testing for tools

### 🟢 Low Priority

- [ ] Add visual testing (if UI added)
  - Screenshot tests
  - Cross-browser tests
  - Responsive design tests
  - Accessibility tests

---

## Documentation

### 🔴 High Priority

- [ ] Complete API documentation
  - Document all tool parameters and returns
  - Add code examples for each tool
  - Document state object fields
  - Add workflow diagrams

- [ ] Add user guide
  - Getting started tutorial
  - Common use cases
  - Troubleshooting guide
  - FAQ section

### 🟡 Medium Priority

- [ ] Create video tutorials
  - Setup and installation
  - Common workflows
  - Advanced features
  - Tips and tricks

- [ ] Add contribution guide
  - Code style guidelines
  - Pull request process
  - Development setup
  - Testing guidelines

### 🟢 Low Priority

- [ ] Add architecture diagrams
  - System architecture
  - Data flow diagrams
  - Component interactions
  - Deployment diagrams

---

## Performance

### 🟡 Medium Priority

- [ ] Optimize file operations
  - Batch file reads
  - Async operations where possible
  - Memory-efficient parsing
  - Lazy loading of large projects

- [ ] Add operation metrics
  - Track execution times
  - Memory usage monitoring
  - Cache hit rates
  - Performance profiling

### 🟢 Low Priority

- [ ] Implement project indexing
  - Build searchable index
  - Fast lookups without parsing
  - Background indexing
  - Incremental index updates

---

## Deployment

### 🟡 Medium Priority

- [ ] Create Docker image
  - Multi-stage build for smaller image
  - Include Ollama or use external
  - Configuration via environment variables
  - Volume mounting for projects

- [ ] Add CI/CD pipelines
  - Automated testing on PRs
  - Automated releases
  - Code quality checks
  - Security scanning

### 🟢 Low Priority

- [ ] Create installation packages
  - PyPI package
  - Wheels for different platforms
  - Installation scripts
  - Systemd service files
