# You can have a README, as a treat

## What is?
It's a silly fedi bot (currently at https://fox.nexus/@treats).

### Possible combinations
An up-to-date calculation of the possible combinations can be found in [the bot's bio on fedi](https://fox.nexus/@treats).

### Options
```
usage: gen.py [-h] [-d] [-c] [--most-interacted COUNT] [--status-count] [-u] [--visibility {private,direct,unlisted,public}] [--no-log] [-v]

Generate a string in the format "{folx} can have {treats}, as a treat" and post it to fedi

options:
  -h, --help            show this help message and exit
  -d, --dry-run         Generate output, but do not post it
  -c, --count           Count the number of possible outputs and exit
  --most-interacted COUNT
                        Find the most interacted with post in the last COUNT statuses, save to a file, and exit
  --status-count        Return the total number of statuses posted by the bot and exit
  -u, --update-bio      Update the bot's bio with the number of possible combinations
  --visibility {private,direct,unlisted,public}
  --no-log              Disable logging
  -v, --verbose         Enable verbose **logging**
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for details on setting up a development environment and contributing new treats/folx.