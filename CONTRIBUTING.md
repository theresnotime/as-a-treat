# Contributing

## Setting up
```bash
# Clone the repo and cd into it, then:
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Copy `config.example.py` to `config.py` and fill in the necessary details.
```python
# Instance API URL
API_URL = ""
# Access token for the fedi bot account
ACCESS_TOKEN = ""
# FTP credentials for uploading logs (if used)
FTP_HOST = ""
FTP_USER = ""
FTP_PASS = ""
# If True, do not upload logs via FTP
DONT_UPLOAD_LOGS = True
# The chance for the treat to become a threat
THREAT_PROBABILITY = 1 / 100
# Local directories for cache and logs
LOCAL_CACHE_DIR = "cache"  # unused
LOCAL_LOGS_DIR = "logs"  # unused
```

## Editing [arrays.py](arrays.py)
The format is "*{folx} can have {treats}, as a treat*", so add items to `FOLX` and/or `TREATS`:

```python
FOLX = [
    "Transfems",
    "Foxgirls",
    [...],
]

TREATS = [
    "a headpat",
    "an anti-trust lawsuit",
    [...],
]
```

### Alternate wording
You can now also add treats with alternate wording. These are represented as JSON objects with `text` and `alt_wording` keys. For example:

```python
TREATS = [
    '{"alt_wording": "True", "text": "can do Arson"}',
    "a headpat",
    [...],
]
```

## Tox
I use `tox` to run tests, check code style and fix formatting. It's a good idea to run it before pushing changes. A GitHub action will also run it on PRs.
```bash
# To run tests:
tox

# To fix formatting etc:
tox -e fix
```


## AI contributions
The contributors to this project believe that AI-assisted code contributions should be avoided where possible for environmental, ethical and code quality reasons - therefore, any contribution that has been *obviously and entirely generated* by AI tools is likely to be rejected.
Further information is available in [AI.md](AI.md).


## Gotchas
- `gen.py` will fail if `config.py` isn't present — you can just copy `config.example.py` to `config.py` while testing. Note that the example config doesn't contain the necessary credentials to actually make a post.
- I <3 trailing commas, and `tox` will get very upset if you forget this :3
