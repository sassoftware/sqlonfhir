# SASFHIR

A Python implementation for evaluating SQL on FHIR view definitions against FHIR resources using FHIRPath expressions.

## Overview

SASFHIR provides functionality to transform FHIR resources into tabular data structures based on SQL on FHIR view definitions. It extends the `fhirpathpy` library with custom functions and handles the conversion of FHIR resources into structured data that can be used for analytics and reporting.

## Features

- **FHIRPath Expression Evaluation**: Evaluates FHIRPath expressions against FHIR resources
- **SQL on FHIR View Processing**: Processes view definitions to extract structured data
- **Union Operations**: Supports `unionAll` operations for combining multiple data sources
- **Conditional Processing**: Handles `where` clauses and conditional logic
- **Column Mapping**: Maps FHIR resource elements to named columns
- **Iteration Support**: Provides `forEach` and `forEachOrNull` operations

## Installation

```bash
pip install sqlonfhir
```

## Dependencies

- `fhirpathpy`: Core FHIRPath evaluation engine
- `antlr4-python3-runtime`: ANTLR runtime for parsing
- `python-dateutil`: Date/time utilities

## Usage

```python
from sqlonfhir import eval

# Define your view definition
view_definition = {
    "resource": "Patient",
    "column": [
        {"name": "id", "path": "id"},
        {"name": "name", "path": "name.given.first()"}
    ]
}

# Your FHIR resources
resources = [
    {
        "resourceType": "Patient",
        "id": "patient1",
        "name": [{"given": ["John"], "family": "Doe"}]
    }
]

# Evaluate the view
result = eval(resources, view_definition)
print(result)
```

## API

### `eval(resources, view_definition)`
Main evaluation function that processes FHIR resources against a view definition.

**Parameters:**
- `resources`: List of FHIR resources to process
- `view_definition`: SQL on FHIR view definition

**Returns:**
- List of dictionaries representing the extracted tabular data

## Testing

Run the test suite:
```bash
uv run pytest
```

Generate test report:
```bash
./generate_test_report.sh
```

## Project Structure

```
sasfhir/
├── sasfhir/
│   ├── __init__.py
│   └── sasfhir.py          # Main implementation
├── tests/
│   ├── resources/          # Test FHIR resources and view definitions
│   └── test.py             # Test suite
├── test_report/           # Test reporting utilities
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Contributing

Maintainers are accepting patches and contributions to this project.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details about submitting contributions to this project.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

Those implementing FHIR projects should ensure they have the appropriate licenses to cover any required third party data standards.
