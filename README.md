# PyPSA dashboard for reserve modeling

Streamlit UI for a simple pypsa toy model that demonstrates how to model spinning reserves.

This tool is licensed under the Creative Commons CC-BY 4.0 license    (<https://creativecommons.org/licenses/by/4.0/>).

## Development

### Setup

After cloning the repository, create a virtual python environment
in a subdirectory `.env` and activate it:

```bash
python -m venv .\.env
.env\Scripts\activate.bat
```

Install the necessary dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

The code is autoformatted and checked with [pre-commit](https://pre-commit.com/).
If you make changes to the code that you want to commit back to the repository,
please install pre-commit with:

```bash
pre-commit install
```

If you have pre-commit installed, every file in a commit is checked to match a
certain style and the commit is stopped if any rules are violated. Before committing,
you can also check your staged files manually by running:

```bash
pre-commit run
```
