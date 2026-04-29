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


def test_no_double_words():
    from arrays import FOLX, TREATS

    for folx in FOLX:
        assert not folx.endswith(" can")
        assert not folx.endswith(" can have")
    for treat in TREATS:
        assert not treat.startswith("have ")
        assert not treat.startswith("can have ")
