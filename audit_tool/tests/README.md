# Audit Tool Tests

This directory contains test files and scripts for the Sopra Steria Brand Audit Tool.

## Test Files

- `test_audit_tool.py` - Comprehensive test suite for all audit tool components
- `test_single_url.txt` - Single URL for quick testing
- `test_urls.txt` - Multiple URLs for batch testing
- `test_persona_simple.md` - Simplified persona file for testing
- `test_output_*/` - Test output directories (generated during testing)

## Running Tests

### Quick Test Suite

```bash
# From the project root directory
cd audit_tool/tests
python test_audit_tool.py
```

### Manual Testing

```bash
# From the project root directory
python -m audit_tool.main --urls audit_tool/tests/test_single_url.txt --persona audit_tool/tests/test_persona_simple.md --output audit_tool/tests/test_output --no-summary
```

### Full Test with Summary

```bash
# From the project root directory
python -m audit_tool.main --urls audit_tool/tests/test_urls.txt --persona audit_inputs/personas/P1.md --output audit_tool/tests/full_test_output --verbose
```

## Test Components

The test suite covers:

1. **YAML Configuration Loading** - Verifies methodology.yaml parsing
2. **Persona Parsing** - Tests persona file parsing and attribute extraction
3. **Web Scraping** - Tests page content fetching and caching
4. **AI Interface** - Tests prompt template loading and formatting
5. **Full Pipeline** - End-to-end audit execution test

## Expected Results

- All core components should pass individual tests
- Full pipeline should generate both hygiene scorecard and experience report
- Average scores should be between 0-10
- Output files should be created in specified directories

## Troubleshooting

If tests fail:

1. Check that you're in the correct directory (project root)
2. Ensure the virtual environment is activated
3. Verify all dependencies are installed (`pip install -r requirements.txt`)
4. Check that API keys are properly configured
5. Ensure internet connectivity for web scraping tests
