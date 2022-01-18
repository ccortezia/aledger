# aledger-app

The primary application component.

## Quick Start

Launch the application using Docker:

```
make run.docker
```

The API is reachable at http://localhost:8000.

The API's live docs can be accessed at http://localhost:8000/docs.

Hint: for quick API exploration, import API client [definitions](resources/aledger-insomnia.json) into [Insomnia](https://insomnia.rest/download).

## Contributing

Install [pyenv](https://github.com/pyenv/pyenv), install the dependencies in a virtualenv, then run the tests:

```
pyenv virtualenv 3.10.0 aledger
pyenv activate aledger
pip install -U pip
pip install -r requirements/requirements.test.txt
pytest
```

Refer to the [code structure overview](docs/code-structure.md) for additional information.
