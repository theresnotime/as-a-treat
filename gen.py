import argparse
import config
import ftplib
import hashlib
import json
import logging
import os
import random
import sys
import time
from arrays import FOLX, TREATS
from datetime import datetime, timezone
from enum import Enum
from mastodon import Mastodon

log = logging.getLogger(__name__)


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
        log.info('Posted: "%s"', status)
        print(f"Posted: {status}")
    else:
        print(f'Dry run: would have posted "{status}"')
        log.info('Dry run: would have posted "%s"', status)


def should_be_threat():
    """Use config.THREAT_PROBABILITY to determine if this treat should be a threat"""
    # TODO: Remove this check once enough time has passed since adding THREAT_PROBABILITY to config
    if not hasattr(config, "THREAT_PROBABILITY"):
        # Warn in the logs and on the console
        log.warning("THREAT_PROBABILITY is not present in config, using old default")
        print("Warning: THREAT_PROBABILITY is not present in config, using old default")
        # Use old default of '1 / 100'
        range_max = int(1 / (1 / 100))
    else:
        range_max = int(1 / config.THREAT_PROBABILITY)
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


def upload_logs(filename: str) -> None:
    """Upload a file to the FTP server"""
    # Check if filename exists
    if not os.path.isfile(filename):
        log.error(f"File {filename} does not exist")
        return
    session = ftplib.FTP(config.FTP_HOST, config.FTP_USER, config.FTP_PASS)
    ftplib.FTP.cwd(session, "as-a-treat")
    file = open(filename, "rb")
    session.storbinary(f"STOR {filename}", file)
    file.close()
    session.quit()
    log.info(f"Uploaded {filename}")


def get_status_count(mastodon: Mastodon) -> int:
    """Get the total number of statuses posted by the bot"""
    account = mastodon.me()
    return account.statuses_count


def most_interacted(over_count: int = 400, cache: bool = True) -> None:
    """Find the most interacted with post and save a link to a file"""
    mastodon = Mastodon(access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL)
    start_time = time.time()
    total_statuses = get_status_count(mastodon)
    print(f"Total statuses: {total_statuses}")
    target_count = over_count
    print(f"Fetching about the last {target_count} statuses...")
    statuses = mastodon.account_statuses(
        id=mastodon.me().id,
        exclude_replies=True,
        exclude_reblogs=True,
        limit=40,
    )
    all_statuses: list = []
    while statuses and len(all_statuses) < target_count:
        all_statuses.extend(statuses)
        if len(all_statuses) >= target_count:
            break
        print(f"Fetched {len(all_statuses)} statuses so far...")
        statuses = mastodon.fetch_next(statuses)
        # Be nice to the server
        if len(all_statuses) % 400 == 0:
            print("Sleeping for 1 second to be nice to the server...")
            time.sleep(1)

    if not all_statuses:
        print("No statuses found")
        return
    print(f"Fetched {len(all_statuses)} statuses and stopping")

    most_interacted_status = max(
        all_statuses,
        key=lambda status: status.reblogs_count + status.favourites_count,
    )
    link = most_interacted_status.url
    end_time = time.time()

    if cache:
        cache_content: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "account_id": mastodon.me().id,
            "account_username": mastodon.me().username,
            "statuses_searched": len(all_statuses),
            "account_total_statuses": total_statuses,
            "most_interacted_status_in_batch": {
                "id": most_interacted_status.id,
                "timestamp": most_interacted_status.created_at.isoformat(),
                "url": most_interacted_status.url,
                "content": most_interacted_status.content,
                "reblogs_count": most_interacted_status.reblogs_count,
                "favourites_count": most_interacted_status.favourites_count,
            },
            "newest_status_id": all_statuses[0].id,
            "oldest_status_id": all_statuses[-1].id,
            "time_taken_seconds": f"{end_time - start_time:.2f}",
            "statuses_count": len(all_statuses),
            "statuses_hash": None,
            "statuses": [],
        }
        for status in all_statuses:
            cache_content["statuses"].append(
                {
                    "id": status.id,
                    "timestamp": status.created_at.isoformat(),
                    "url": status.url,
                    "content": status.content,
                    "reblogs_count": status.reblogs_count,
                    "favourites_count": status.favourites_count,
                }
            )
        # Generate a hash of cache_content["statuses"] for cache key
        hasher = hashlib.sha256()
        hasher.update(json.dumps(cache_content["statuses"], sort_keys=True).encode())
        cache_content["statuses_hash"] = hasher.hexdigest()

        cache_content = {**cache_content}

        # If the cache file exists, copy it to a backup
        if os.path.isfile("statuses_cache.json"):
            os.rename("statuses_cache.json", "statuses_cache.backup.json")

        # Write the cache to a file
        with open("statuses_cache.json", "w") as f:
            f.write(json.dumps(cache_content, indent=4))
        print("Wrote cache to statuses_cache.json")

    print(
        f"Checked {len(all_statuses)} statuses in {end_time - start_time:.2f} seconds"
    )
    print(f"Most interacted post: {link}")
    print(
        f"Boosts: {most_interacted_status.reblogs_count}, Favourites: {most_interacted_status.favourites_count}"
    )
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "id": most_interacted_status.id,
        "post_timestamp": most_interacted_status.created_at.isoformat(),
        "url": most_interacted_status.url,
        "content": most_interacted_status.content,
        "reblogs_count": most_interacted_status.reblogs_count,
        "favourites_count": most_interacted_status.favourites_count,
        "statuses_searched": len(all_statuses),
        "account_total_statuses": total_statuses,
    }
    with open("most_interacted.json", "w") as f:
        f.write(json.dumps(result, indent=4))
    log.info("Most interacted post: %s", link)


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
        "--most-interacted",
        action="store",
        help="Find the most interacted with post in the last COUNT statuses, save to a file, and exit",
        type=int,
        metavar="COUNT",
    )
    parser.add_argument(
        "--status-count",
        action="store_true",
        help="Return the total number of statuses posted by the bot and exit",
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

    if args.status_count:
        mastodon = Mastodon(
            access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL
        )
        total_statuses = get_status_count(mastodon)
        print(total_statuses)
        sys.exit(0)

    if args.most_interacted:
        check_count = int(args.most_interacted)
        most_interacted(check_count)
        sys.exit(0)

    used_folx = get_used("folx")
    used_treats = get_used("treats")

    # Remove previously used folx
    available_folx = [item for item in FOLX if item not in used_folx]
    log.debug("%d unused folx remaining", len(available_folx))
    if len(available_folx) == 0:
        available_folx = FOLX
        clear_used("folx")

    available_treats = [item for item in TREATS if item not in used_treats]
    log.debug("%d unused treats remaining", len(available_treats))
    if len(available_treats) == 0:
        available_treats = TREATS
        clear_used("treats")

    # Totally pointless shuffle :3
    random.shuffle(available_treats)
    random.shuffle(available_folx)

    # Choose a random folx and treat from the remaining available options
    folx = random.choice(available_folx)
    treat = random.choice(available_treats)

    # Handle 'alternate wording' treats
    if treat.startswith("{") and treat.endswith("}"):
        if json.loads(treat).get("alt_wording") == "True" and "text" in json.loads(
            treat
        ):
            alt_wording = True
            treat_text = json.loads(treat)["text"]
            log.debug('Using alternate wording for treat: "%s"', treat_text)
        else:
            # Something went wrong with the formatting
            log.error("Treat formatting error - invalid JSON: %s", treat)
            sys.exit(1)
    else:
        alt_wording = False
        treat_text = treat

    log.debug('Picked folx "%s" and treat "%s"', folx, treat_text)

    # Save the chosen folx and treat so they can't be picked again
    save_used("folx", folx)
    save_used("treats", treat)

    treat_or_threat = "threat" if should_be_threat() else "treat"

    if alt_wording:
        status = f"{folx} {treat_text}, as a {treat_or_threat}"
    else:
        status = f"{folx} can have {treat_text}, as a {treat_or_threat}"

    write_status(status, args.dry_run, args.visibility)

    # Upload logs
    if config.DONT_UPLOAD_LOGS:
        print("Not uploading logs as DONT_UPLOAD_LOGS is True")
    else:
        log.info("Uploading logs...")
        upload_logs("used_folx")
        upload_logs("used_treats")
        upload_logs("as-a-treat.log")
        log.info("Finished uploading logs")
