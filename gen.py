import config
import getopt
import os
import random
import sys
from arrays import FOLX, TREATS
from mastodon import Mastodon


def write_status(status: str, dry_run: bool = False) -> None:
    """Write a status to Mastodon"""
    mastodon = Mastodon(access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL)
    if dry_run is False:
        # Post
        mastodon.status_post(status=status, visibility="unlisted")
        print(f"Posted {status}")
    else:
        print(f"Dry run, would have posted {status}")


def get_last(thing: str):
    if os.path.isfile(f"last_{thing}"):
        return open(f"last_{thing}", "r").readline()
    else:
        return None


def save_last(thing: str, value: str) -> None:
    with open(f"last_{thing}", "w") as f:
        f.write(value)


if __name__ == "__main__":
    dry_run = False
    opts, args = getopt.getopt(sys.argv[1:], shortopts="d", longopts="dry-run")
    for opt, arg in opts:
        if opt in ("-d", "--dry-run"):
            dry_run = True

    # Get last folx and treat choices
    last_folx = get_last("folx")
    last_treat = get_last("treat")

    # Choose a random folx and treat, removing the last choices
    if last_folx:
        FOLX.remove(last_folx)
    if last_treat:
        TREATS.remove(last_treat)
    folx = random.choice(FOLX)
    treat = random.choice(TREATS)

    # Save the last folx and treat choices
    save_last("folx", folx)
    save_last("treat", treat)

    status = f"{folx} can have {treat}, as a treat"
    write_status(status, dry_run)
