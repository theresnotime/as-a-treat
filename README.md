# You can have a README, as a treat

## What is?
It's a silly fedi bot (currently at https://fox.nexus/@treats).

<!--### Possible combinations
There are 99 folx and 176 treats, resulting in 17,424 possible combinations.

## Contributing
### Setting up
```bash
# Clone the repo and cd into it, then:
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Editing [arrays.py](arrays.py)
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

### Tox
I use `tox` to run tests, check code style and fix formatting. It's a good idea to run it before pushing changes. A GitHub action will also run it on PRs.
```bash
# To run tests:
tox

# To fix formatting etc:
tox -e fix
```

### Gotchas
- `gen.py` will fail if `config.py` isn't present — you can just copy `config.example.py` to `config.py` while testing. Note that the example config doesn't contain the necessary credentials to actually make a post.
- I <3 trailing commas, and `tox` will get very upset if you forget this :3 
