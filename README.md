# pcil
A python CLI tool used to generate a single header C++ library for getting PCI device names.

### Arguments

| Argument | Description | Example |
| --- | --- | --- |
| -i/--in | Path to file containing the ids database | pci.ids |
| -o/--out | Path to write the generated header file to | pcil.hpp |
| -q/--quiet | Suppress status messages | (no value) |
| -u/--url | URL to fetch ids database from. (Optional) | https://www.example.com/pci.ids |
