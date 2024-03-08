from pathlib import Path


def test_unique():
    seen = set()
    for line in Path("arrays.py").read_text().split("\n"):
        if line.strip() == line:
            # No leading indentation, not a list entry
            if line == "]":
                # This is the end of a list. Clear seen, so same entries
                # can be on both lists.
                seen = set()
            continue
        assert line not in seen
        seen.add(line)
