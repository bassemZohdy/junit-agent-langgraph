# JUnit Agent LangGraph - Installation Guide

**Version**: 1.0.0
**Last Updated**: February 21, 2026

This guide provides step-by-step instructions for installing and configuring JUnit Agent LangGraph on your system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)
7. [Uninstallation](#uninstallation)

---

## Prerequisites

Before installing JUnit Agent LangGraph, ensure your system meets the following requirements:

### Required Software

| Software | Version | Purpose | How to Check |
|----------|---------|---------|--------------|
| **Python** | 3.8 or higher | Runtime environment | `python --version` |
| **pip** | Latest | Package manager | `pip --version` |
| **Ollama** | Latest | LLM backend | `ollama --version` |
| **Java JDK** | 8 or higher | Java project support | `javac --version` |
| **Maven** | 3.6+ | Java build tool | `mvn --version` |

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10+
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk Space**: 500MB for installation + space for Java projects
- **Network**: Internet connection for initial setup and Ollama model downloads

### Checking Prerequisites

#### Check Python Version

```bash
python --version
# or
python3 --version
```

Expected output: `Python 3.8.x` or higher

If Python is not installed or is an older version:
- **Linux**: `sudo apt-get install python3.11` (Ubuntu/Debian)
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

#### Check Ollama

```bash
ollama --version
```

If Ollama is not installed:
- Download from [ollama.com](https://ollama.com/download)
- Follow the installation instructions for your OS

#### Check Java

```bash
javac --version
```

If Java is not installed:
- **Linux**: `sudo apt-get install default-jdk` (Ubuntu/Debian)
- **macOS**: `brew install openjdk@17`
- **Windows**: Download from [oracle.com](https://www.oracle.com/java/technologies/downloads/)

#### Check Maven

```bash
mvn --version
```

If Maven is not installed:
- **Linux**: `sudo apt-get install maven` (Ubuntu/Debian)
- **macOS**: `brew install maven`
- **Windows**: Download from [maven.apache.org](https://maven.apache.org/download.cgi)

---

## Installation

### Quick Install (Recommended)

The quickest way to install JUnit Agent is using the provided installation scripts.

#### Linux/macOS

```bash
# Navigate to the project directory
cd junit-agent-langgraph

# Run the installation script
chmod +x dist/scripts/install.sh
./dist/scripts/install.sh
```

The script will:
1. Check Python version
2. Verify Ollama installation
3. Create a virtual environment
4. Install all dependencies
5. Set up the package

#### Windows (PowerShell)

```powershell
# Navigate to the project directory
cd junit-agent-langgraph

# Run the installation script
.\dist\scripts\install.ps1
```

### Manual Installation

If you prefer manual installation or need more control:

#### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/junit-agent/junit-agent-langgraph.git
cd junit-agent-langgraph
```

#### Step 2: Create a Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Step 3: Install Dependencies

```bash
# Install from requirements
pip install --upgrade pip
pip install -r requirements.txt

# Or install the package in development mode
pip install -e .
```

#### Step 4: Install Additional Dependencies (Optional)

For development and security tools:

```bash
pip install -e ".[dev,security]"
```

This includes:
- pytest (testing)
- pytest-cov (coverage)
- black, isort (code formatting)
- mypy (type checking)
- ruff (linting)
- bandit, safety (security scanning)

### Installation from Source

If you want to modify the source code:

```bash
# Clone the repository
git clone https://github.com/junit-agent/junit-agent-langgraph.git
cd junit-agent-langgraph

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .
```

---

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
# Linux/macOS
cp dist/config/example.env .env

# Windows
copy dist\config\example.env .env
```

### Step 2: Configure Ollama Model

Edit the `.env` file and set your preferred Ollama model:

```bash
# Available models: llama3.2, mistral, codellama, etc.
OLLAMA_MODEL=llama3.2
```

**Important**: Make sure to download the model if you haven't already:

```bash
ollama pull llama3.2
```

### Step 3: Configure Ollama Connection

If Ollama is running on a different host or port:

```bash
OLLAMA_BASE_URL=http://your-host:port
```

### Step 4: Adjust Timeouts (Optional)

For large projects, you may need to increase timeouts:

```bash
LLM_TIMEOUT_SECONDS=300
MAVEN_TIMEOUT_SECONDS=600
```

### Step 5: Configure Logging (Optional)

```bash
LOG_LEVEL=INFO
LOG_FILE=junit-agent.log
```

### Complete Configuration Reference

| Variable | Description | Default | Recommended Range |
|----------|-------------|---------|-------------------|
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` | - |
| `OLLAMA_MODEL` | LLM model name | `llama3.2` | `llama3.2`, `mistral`, `codellama` |
| `OLLAMA_TEMPERATURE` | Creativity level | `0.7` | `0.0-2.0` |
| `OLLAMA_MAX_TOKENS` | Max response tokens | `4096` | `2048-8192` |
| `LLM_TIMEOUT_SECONDS` | LLM request timeout | `120` | `60-600` |
| `MAVEN_TIMEOUT_SECONDS` | Maven command timeout | `300` | `60-1200` |
| `MAX_RETRIES` | Max retry attempts | `3` | `1-5` |
| `CACHE_ENABLED` | Enable caching | `true` | `true/false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG/INFO/WARNING/ERROR` |

---

## Verification

### Run Validation Script

After installation, verify everything is working:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Run validation
python dist/scripts/validate_install.py
```

Expected output:
```
============================================================
  JUnit Agent LangGraph - Installation Validation
============================================================

✓ Checking Python version...
  Python 3.11.2
  ✅ PASS: Python version is compatible

✓ Checking dependencies...
  ✅ langchain
  ✅ langchain_core
  ✅ langchain_ollama
  ✅ langgraph
  ✅ pydantic
  ✅ javalang
  ✅ ollama
  ✅ rich

✓ Checking configuration module...
  ✅ Configuration module is accessible
     Ollama URL: http://localhost:11434
     Ollama Model: llama3.2

...

============================================================
  ✅ All checks passed! Installation is valid.
============================================================
```

### Test Basic Functionality

```bash
# Test basic import
python -c "from src.config import settings; print('Configuration loaded')"

# Test agent import
python -c "from src.agents.base import BaseAgent; print('Agent loaded')"
```

### Run Example on Sample Project

The repository includes sample projects for testing:

```bash
# Navigate to a sample project
cd tests/samples/junit4-sample

# Run JUnit Agent on it
junit-agent --project-path .
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Python not found"

**Symptom**: Installation script fails with "Python not found"

**Solution**:
1. Check if Python is installed: `python --version`
2. If not, install Python 3.8+ from [python.org](https://www.python.org/downloads/)
3. Add Python to your PATH (Windows)
4. Use `python3` instead of `python` if both are installed

#### Issue: "Ollama connection refused"

**Symptom**: Cannot connect to Ollama during installation or runtime

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `ollama list`
3. Verify `OLLAMA_BASE_URL` in `.env` matches Ollama's address
4. Check firewall settings are not blocking connections

#### Issue: "Module not found" errors

**Symptom**: Import errors when running JUnit Agent

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -e .`
3. Check PYTHONPATH includes the project directory
4. Try running from the project root directory

#### Issue: "Permission denied" errors

**Symptom**: Cannot write files or execute scripts

**Solution**:
- **Linux/macOS**:
  ```bash
  chmod +x dist/scripts/*.sh
  sudo chown -R $USER:$USER venv
  ```

- **Windows**: Run PowerShell as Administrator

#### Issue: Tests fail after installation

**Symptom**: Validation script shows failed tests

**Solution**:
1. Check test report: `test_report.md`
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Update pip: `pip install --upgrade pip`
4. Clear cache: `pip cache purge`

### Getting Help

If you encounter issues not covered here:

1. **Check the Documentation**: [GitHub Wiki](https://github.com/junit-agent/junit-agent-langgraph/wiki)
2. **Search Issues**: [GitHub Issues](https://github.com/junit-agent/junit-agent-langgraph/issues)
3. **Ask in Discussions**: [GitHub Discussions](https://github.com/junit-agent/junit-agent-langgraph/discussions)
4. **Create an Issue**: Provide detailed information:
   - Operating system and version
   - Python version
   - Error messages
   - Steps to reproduce

---

## Advanced Configuration

### Customizing Test Generation

#### Adjust LLM Temperature

Higher temperature = more creative tests, lower = more deterministic:

```bash
# For consistent, predictable tests
OLLAMA_TEMPERATURE=0.3

# For varied, exploratory tests
OLLAMA_TEMPERATURE=1.0
```

#### Increase Max Tokens

For complex classes requiring longer test code:

```bash
OLLAMA_MAX_TOKENS=8192
```

### Performance Optimization

#### Enable Caching

Caching improves performance on repeated operations:

```bash
CACHE_ENABLED=true
```

#### Enable Parallel Operations

For faster processing on multi-core systems (experimental):

```bash
PARALLEL_FILE_OPERATIONS=true
```

### Security Considerations

#### Disable Telemetry (if implemented)

```bash
# Add to .env if needed
TELEMETRY_ENABLED=false
```

#### Use Read-Only Mode

Prevent accidental file modifications:

```bash
READ_ONLY_MODE=true
```

### Integration with CI/CD

#### Environment-Specific Configuration

Create multiple `.env` files:

```bash
# .env.development
LOG_LEVEL=DEBUG

# .env.production
LOG_LEVEL=WARNING

# Use with:
cp .env.production .env
```

#### Docker Integration

See `dist/README.md` for Docker setup instructions (if available).

---

## Uninstallation

### Linux/macOS

Run the uninstall script:

```bash
./dist/scripts/uninstall.sh
```

Or manually:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove configuration (optional)
rm .env

# Remove logs (optional)
rm *.log
```

### Windows

Remove the virtual environment manually:

```powershell
# Deactivate virtual environment
deactivate

# Remove virtual environment
Remove-Item -Recurse -Force venv

# Remove configuration (optional)
Remove-Item .env

# Remove logs (optional)
Remove-Item *.log
```

### Complete Cleanup

To remove all JUnit Agent files and configurations:

```bash
# Linux/macOS
rm -rf venv .env *.log dist/
git clean -fdx  # If in git repository

# Windows
Remove-Item -Recurse -Force venv, .env, *.log, dist
```

---

## Next Steps

After successful installation:

1. **Read the User Guide**: [USER_GUIDE.md](../USER_GUIDE.md)
2. **Explore Examples**: Check `tests/samples/` for example projects
3. **Generate Your First Tests**:
   ```bash
   junit-agent --project-path /path/to/your/java/project
   ```
4. **Customize Configuration**: Edit `.env` for your needs
5. **Explore Advanced Features**: See API documentation

---

## Additional Resources

- **Main README**: [README.md](../README.md)
- **API Documentation**: [API.md](../API.md)
- **User Guide**: [USER_GUIDE.md](../USER_GUIDE.md)
- **Test Report**: [test_report.md](../test_report.md)
- **GitHub Repository**: [github.com/junit-agent/junit-agent-langgraph](https://github.com/junit-agent/junit-agent-langgraph)

---

**Version**: 1.0.0
**Last Updated**: February 21, 2026
**Maintained By**: JUnit Agent Team
