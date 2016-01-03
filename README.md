# rst2ansi

A python module dedicated to rendering RST (reStructuredText) documents
to ansi-escaped strings suitable for display in a terminal.

## Usage

### As a CLI utility:

```bash
usage: rst2ansi [-h] [file]

Prints a reStructuredText input in an ansi-decorated format suitable for
console output.

positional arguments:
  file        A path to the file to open

optional arguments:
  -h, --help  show this help message and exit
```

### As a python module:

```bash
from rst2ansi import rst2ansi

print(rst2ansi('I **love** reStructuredText!'))
```
