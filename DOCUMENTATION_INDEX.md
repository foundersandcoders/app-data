# Documentation Index

This document provides an overview of all documentation in this repository.

## Quick Start

1. **New users**: Start with [README.md](README.md)
2. **Developers**: Read [REFACTORING.md](REFACTORING.md) and [CLAUDE.md](CLAUDE.md)
3. **File discovery issues**: See [FILE_DISCOVERY.md](FILE_DISCOVERY.md)

## Documentation Files

### User Documentation

**[README.md](README.md)** - Main documentation
- Overview of all scripts
- Usage examples
- Command-line options
- Output formats
- Troubleshooting

### Technical Documentation

**[FILE_DISCOVERY.md](FILE_DISCOVERY.md)** - Intelligent file discovery
- How automatic file discovery works
- Filename parsing rules
- Sorting algorithm
- Examples and testing
- Troubleshooting file selection

**[REFACTORING.md](REFACTORING.md)** - Code refactoring details
- Summary of improvements made
- Before/after comparisons
- Code quality metrics
- Architecture overview
- Migration notes

**[ARGUMENT_ORDER_CHANGE.md](ARGUMENT_ORDER_CHANGE.md)** - Argument order update
- New command-line argument order
- Rationale for the change
- Migration guide
- Backward compatibility
- Testing verification

### Development Documentation

**[CLAUDE.md](CLAUDE.md)** - Instructions for Claude Code
- Development workflow (TDD)
- Code quality standards
- Git workflow
- Commit message conventions
- Pull request process

**[requirements.txt](requirements.txt)** - Development dependencies
- pytest for testing
- mypy for type checking
- black for formatting
- flake8 for linting

## Code Files

### Main Scripts

- **vacancies.py** - Extract and analyse vacancy data
- **starts.py** - Extract and analyse starts data
- **monthly.py** - Extract and analyse monthly starts data

### Shared Modules

- **utils.py** - Shared utility functions
  - Name cleaning
  - File discovery
  - Table formatting
  - CSV reading

- **config.py** - Configuration constants
  - Thresholds
  - Field names
  - File patterns
  - Column widths

### Test Files

- **test_utils.py** - Unit tests for utility functions
  - Name cleaning tests
  - Position parsing tests
  - Year/quarter extraction tests
  - Table formatting tests

- **test_file_discovery.py** - File discovery tests
  - Year/quarter parsing tests
  - File sorting tests
  - Cross-year sorting tests
  - Integration tests

## Documentation by Use Case

### "I want to run the scripts"
→ [README.md](README.md) - Usage section

### "I want to understand how file discovery works"
→ [FILE_DISCOVERY.md](FILE_DISCOVERY.md)

### "I want to modify the code"
→ [REFACTORING.md](REFACTORING.md) + [CLAUDE.md](CLAUDE.md)

### "The script is using the wrong file"
→ [FILE_DISCOVERY.md](FILE_DISCOVERY.md) - Troubleshooting section

### "I want to change thresholds or settings"
→ [README.md](README.md) - Configuration section

### "I want to add tests"
→ [CLAUDE.md](CLAUDE.md) - Testing section

### "I want to understand the refactoring"
→ [REFACTORING.md](REFACTORING.md)

## File Structure Summary

```
.
├── README.md                    # Main documentation
├── CLAUDE.md                    # Claude Code instructions
├── REFACTORING.md               # Refactoring details
├── FILE_DISCOVERY.md            # File discovery documentation
├── DOCUMENTATION_INDEX.md       # This file
├── requirements.txt             # Python dependencies
│
├── vacancies.py                 # Vacancy analysis script
├── starts.py                    # Starts analysis script
├── monthly.py                   # Monthly analysis script
│
├── utils.py                     # Shared utilities
├── config.py                    # Configuration
│
├── test_utils.py                # Unit tests
├── test_file_discovery.py       # File discovery tests
│
└── demo_file_discovery.sh       # Interactive demo
```

## Quick Reference

### Running Scripts
```bash
python3 vacancies.py              # Latest vacancy data
python3 starts.py ST0116          # Latest starts data
python3 monthly.py                # Latest monthly data
```

### Running Tests
```bash
python3 test_utils.py             # Unit tests
python3 test_file_discovery.py    # File discovery tests
pytest test_*.py -v               # All tests (if pytest installed)
```

### Getting Help
```bash
python3 vacancies.py --help       # Script help
python3 starts.py --help          # Script help
python3 monthly.py --help         # Script help
```

## Version History

### Latest (Current)
- ✅ Intelligent file discovery with year/quarter parsing
- ✅ Comprehensive refactoring for maintainability
- ✅ Full test coverage
- ✅ Complete documentation

### Original
- ❌ Manual file selection
- ❌ Code duplication
- ❌ No tests
- ❌ Minimal documentation

See [REFACTORING.md](REFACTORING.md) for detailed changes.
