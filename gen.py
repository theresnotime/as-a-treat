import config
import getopt
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


if __name__ == "__main__":
    dry_run = False
    opts, args = getopt.getopt(sys.argv[1:], shortopts="d", longopts="dry-run")
    for opt, arg in opts:
        if opt in ("-d", "--dry-run"):
            dry_run = True
    status = f"{random.choice(FOLX)} can have {random.choice(TREATS)}, as a treat"
    write_status(status, dry_run)
