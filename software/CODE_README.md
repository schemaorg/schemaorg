# Schema.org Code

This document contains recommendations for the code of the schema.org project.

## Python

We recommend following the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). We recommend the following:

* Use [PEP-484](https://peps.python.org/pep-0484/) style type definition for functions.
* Use context managers for file operations and locking.
* Keep the code as platform agnostic as possible, use the relevant Python functionalities for system, terminal interactions.
* Use the logging package for all logging output (no prints).
* Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting.
* When possible, use the default Python packages, be mindful when adding new dependencies.


## Style

### File layout

- Have all imports at the beginning of the file.
- Imports grouped into blocks separated by a newline, and each block has its imports lexicographically sorted.
  The groups are in this order:
    1. any imports from a regular Python install, or that are from required dependencies
    2. only if needed, the stanza to amend the sys.path to load local packages
    3. the imports for the packages defined in this schemaorg codebase.
- general blocks in the file (import block, function, etc.) are separated by 2 empty lines.
