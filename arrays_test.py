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


def test_alt_wording_syntax():
    import json
    from arrays import TREATS
    from json import JSONDecodeError
    from pytest import fail

    json_treats = [
        treat for treat in TREATS if treat.startswith("{") and treat.endswith("}")
    ]
    for treat in json_treats:
        try:
            parsed = json.loads(treat)
            if parsed.get("alt_wording") != "True":
                fail('treat "' + treat + '" does not set "alt_wording" to "True"')
            if parsed.get("text") is None:
                fail('treat "' + treat + '" does not have a "text" attribute')
        except JSONDecodeError:
            fail('treat "' + treat + '" is not a valid json string')
