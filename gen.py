import argparse
import config
import os
import random
import sys
from arrays import FOLX, TREATS
from mastodon import Mastodon

# The chance for the treat to become a threat
THREAT_PROBABILITY = 1 / 100


def count_combinations() -> None:
    """Calculate the number of possible outputs"""
    num_folx = len(FOLX)
    num_treats = len(TREATS)
    combinations = num_folx * num_treats
    print(
        f"There are {num_folx} folx and {num_treats} treats, resulting in {combinations} possible combinations."
    )


def write_status(status: str, dry_run: bool = False) -> None:
    """Write a status to Mastodon"""
    mastodon = Mastodon(access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL)
    if dry_run is False:
        # Post
        mastodon.status_post(status=status, visibility="unlisted")
        print(f"Posted {status}")
    else:
        print(f"Dry run, would have posted {status}")


def should_be_threat():
    """Use THREAT_PROBABILITY to determine if this treat should be a threat"""
    range_max = int(1 / THREAT_PROBABILITY)
    return random.randint(1, range_max) == range_max


def get_last(thing: str):
    if os.path.isfile(f"last_{thing}"):
        return open(f"last_{thing}", "r").readline()
    else:
        return None


def save_last(thing: str, value: str) -> None:
    with open(f"last_{thing}", "w") as f:
        f.write(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate a string in the format "{folx} can have {treats}, as a treat" and post it to fedi'
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Generate output, but do not post it",
    )
    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Count the number of possible outputs and exit",
    )
    args = parser.parse_args()

    if args.count:
        count_combinations()
        sys.exit(0)

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

    treat_or_threat = "threat" if should_be_threat() else "treat"

    status = f"{folx} can have {treat}, as a {treat_or_threat}"
    write_status(status, args.dry_run)
