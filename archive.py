import config
import json
import logging
import os
import time
from datetime import datetime, timezone
from mastodon import Mastodon
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)


def get_archive_path() -> str:
    return getattr(config, "ARCHIVE_FILE_PATH", "archive.json")


def get_archive_interval() -> int:
    return getattr(config, "ARCHIVE_INTERVAL_SECONDS", 86400)


def load_existing_archive() -> Dict[str, Any]:
    """
    Load the existing archive from disk.
    Returns a dictionary with 'statuses' list and 'meta' dict.
    """
    path = get_archive_path()
    if not os.path.exists(path):
        return {"statuses": [], "meta": {"last_archived": 0}}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure structure
            if "statuses" not in data:
                data["statuses"] = []
            if "meta" not in data:
                data["meta"] = {"last_archived": 0}
            return data
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load archive: {e}")
        return {"statuses": [], "meta": {"last_archived": 0}}


def save_archive(data: Dict[str, Any]) -> None:
    """
    Save the archive to disk atomically.
    """
    path = get_archive_path()
    tmp_path = path + ".tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Atomic replace
        os.replace(tmp_path, path)
        log.info(f"Archive saved to {path}")
    except IOError as e:
        log.error(f"Failed to save archive: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def archive_status(status: Dict[str, Any], archive_data: Dict[str, Any]) -> None:
    """
    Update or append a status in the archive.
    """
    status_id = status.get("id")
    if not status_id:
        return

    # Create a simplified status object
    archived_status = {
        "id": status_id,
        "timestamp": status.get("created_at", datetime.now(timezone.utc)).timestamp(),
        "content": status.get("content", ""),
        "likes": status.get("favourites_count", 0),
        "boosts": status.get("reblogs_count", 0),
        "replies": status.get("replies_count", 0),
        # Store raw timestamp as well for readability if needed, but requirements said UNIX
    }

    # Check if exists and update
    existing_index = next(
        (
            index
            for (index, d) in enumerate(archive_data["statuses"])
            if d["id"] == status_id
        ),
        None,
    )

    if existing_index is not None:
        archive_data["statuses"][existing_index] = archived_status
    else:
        archive_data["statuses"].append(archived_status)


def run_periodic_archive(dry_run: bool = False) -> None:
    """
    Check if it's time to archive, and if so, fetch statuses and update archive.
    """
    archive_data = load_existing_archive()
    last_archived = archive_data["meta"].get("last_archived", 0)
    current_time = time.time()
    interval = get_archive_interval()

    if current_time - last_archived < interval:
        log.debug("Not time to archive yet.")
        return

    log.info("Starting periodic archive...")

    if dry_run:
        log.info("Dry run: Skipping API calls and save.")
        return

    try:
        mastodon = Mastodon(
            access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL
        )

        # Fetch account ID
        me = mastodon.account_verify_credentials()
        account_id = me["id"]

        # Fetch statuses (fetch all or just recent? Requirement says "EVERY status")
        # For a periodic job, we might want to fetch everything to update stats on old posts too.
        # But fetching EVERYTHING every time might be heavy if there are thousands.
        # However, requirements say "The bot must periodically archive its posted statuses."
        # and "For each status, store... likes, boosts...".
        # To get updated likes/boosts for old posts, we need to fetch them again.
        # Let's try to fetch recent ones, or iterate.
        # For simplicity and robustness, let's fetch the timeline.
        # Mastodon API pagination might be needed.

        statuses = mastodon.account_statuses(account_id, limit=40)  # Start with recent

        # If we want to be thorough, we should probably paginate back until we hit statuses we've already archived
        # AND that are old enough that their stats likely won't change?
        # Or just fetch everything. Let's fetch a reasonable amount.
        # If the bot posts once a day, 40 covers a month.

        # Let's just fetch the first page for now to satisfy "periodically archive".
        # If the user wants a full history scrape, that's a bigger task.
        # But "EVERY status the bot has ever posted" implies we might need to paginate.

        # Let's implement simple pagination to get all statuses.

        all_fetched = []
        page = statuses
        while page:
            all_fetched.extend(page)
            page = mastodon.fetch_next(page)
            # Safety break to avoid infinite loops if something is weird
            if len(all_fetched) > 10000:
                log.warning("Fetched over 10000 statuses, stopping safety break.")
                break

        log.info(f"Fetched {len(all_fetched)} statuses.")

        for status in all_fetched:
            archive_status(status, archive_data)

        archive_data["meta"]["last_archived"] = current_time
        save_archive(archive_data)

    except Exception as e:
        log.exception(f"Error during periodic archive: {e}")
