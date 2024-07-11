import argparse
import config
import logging
import os
import random
import sys
from arrays import FOLX, TREATS
from datetime import datetime, timezone
from enum import Enum
from mastodon import Mastodon

log = logging.getLogger(__name__)

# The chance for the treat to become a threat
THREAT_PROBABILITY = 1 / 100


class Visibility(Enum):
    """The possible visibilities for a post according to the mastodon client"""

    private = "private"
    direct = "direct"
    unlisted = "unlisted"
    public = "public"

    def __str__(self: "Visibility") -> str:
        return self.value


def get_log_level(no_log: bool, verbose: bool) -> int:
    if no_log:
        return logging.ERROR
    elif verbose:
        return logging.DEBUG
    else:
        return logging.INFO


def count_combinations() -> None:
    """Calculate the number of possible outputs"""
    num_folx = len(FOLX)
    num_treats = len(TREATS)
    combinations = num_folx * num_treats
    output = f"There are {num_folx} folx and {num_treats} treats, resulting in {combinations:,} possible combinations."
    log.info(output)
    print(output)


def update_bio(dry_run: bool = False) -> None:
    """Update the bot's bio with the number of possible combinations"""
    num_folx = len(FOLX)
    num_treats = len(TREATS)
    combinations = num_folx * num_treats
    last_update = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    bio = f"You can have another bot, as a treat.\n\nI can choose from {num_folx} folx and {num_treats} treats, so there are {combinations:,} possible combinations.\n\nI last updated this bio on {last_update} (UTC)."

    if dry_run is False:
        mastodon = Mastodon(
            access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL
        )
        mastodon.account_update_credentials(note=bio)
        log.info("Updated bio to: %s", bio)
        print(f"Updated bio to: {bio}")
    else:
        print(f"Dry run, would have updated bio to: {bio}")
        log.info("Dry run, would have updated bio to: %s", bio)


def write_status(
    status: str, dry_run: bool = False, visibility: Visibility = Visibility("unlisted")
) -> None:
    """Write a status to Mastodon"""
    if dry_run is False:
        # Post
        mastodon = Mastodon(
            access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL
        )
        mastodon.status_post(status=status, visibility=str(visibility))
        log.info('Posted "%s"', status)
        print(f"Posted {status}")
    else:
        print(f"Dry run, would have posted {status}")
        log.info('Dry run, would have posted "%s"', status)


def should_be_threat():
    """Use THREAT_PROBABILITY to determine if this treat should be a threat"""
    range_max = int(1 / THREAT_PROBABILITY)
    chosen_value = random.randint(1, range_max)
    log.debug("Treat/Threat value %d (threat requires %d)", chosen_value, range_max)

    is_threat = chosen_value == range_max
    if is_threat:
        log.debug("Post will be a threat")
    else:
        log.debug("Post will be a treat")

    return is_threat


def get_used_filename(thing: str) -> str:
    """Get the filename for the file containing used _things_"""
    return f"used_{thing}"


def save_used(thing: str, value: str) -> None:
    """Add an entry to the used _things_ list"""
    filename = get_used_filename(thing)
    with open(filename, "a") as f:
        f.write(value + "\n")


def get_used(thing: str) -> list[str]:
    """Get the list of used _things_"""
    filename = get_used_filename(thing)
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return f.read().splitlines()
    else:
        return []


def clear_used(thing: str) -> None:
    """Clear the list of used _things_"""
    filename = get_used_filename(thing)
    with open(filename, "w") as f:
        f.write("")
    log.info("Cleared used %s list", thing)


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
    parser.add_argument(
        "-u",
        "--update-bio",
        action="store_true",
        help="Update the bot's bio with the number of possible combinations",
    )
    parser.add_argument(
        "--visibility",
        type=Visibility,
        choices=list(Visibility),
        action="store",
        default="unlisted",
    )
    parser.add_argument("--no-log", action="store_true", help="Disable logging")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    log_level = get_log_level(args.no_log, args.verbose)
    log_format = "%(asctime)s %(levelname)-5s %(message)s"
    logging.basicConfig(filename="as-a-treat.log", level=log_level, format=log_format)

    if args.count:
        count_combinations()
        sys.exit(0)

    if args.update_bio:
        update_bio(args.dry_run)
        sys.exit(0)

    used_folx = get_used("folx")
    used_treats = get_used("treats")

    # Remove previously used folx
    available_folx = [item for item in FOLX if item not in used_folx]
    log.debug("%d unused folx remaining", len(available_folx))
    if len(available_folx) == 0:
        available_folx = FOLX
        clear_used("folx")

    # Remove previously used treats
    available_treats = [item for item in TREATS if item not in used_treats]
    log.debug("%d unused treats remaining", len(available_treats))
    if len(available_treats) == 0:
        available_treats = TREATS
        clear_used("treats")

    # Choose a random folx and treat from the remaining available options
    folx = random.choice(available_folx)
    treat = random.choice(available_treats)
    log.debug('Chose folx "%s" and treat "%s"', folx, treat)

    # Save the chosen folx and treat so they can't be picked again
    save_used("folx", folx)
    save_used("treats", treat)

    treat_or_threat = "threat" if should_be_threat() else "treat"

    status = f"{folx} can have {treat}, as a {treat_or_threat}"
    write_status(status, args.dry_run, args.visibility)
