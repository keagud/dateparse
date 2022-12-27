import re
from itertools import chain


def iter_all_matches(
    text: str, patterns: list[re.Pattern[str]] | list[str], reverse: bool = False
):

    """
    Yield all matches for any of the given patterns in the text, iterating left to right,
    or right to left if reversed is specified."""

    comp_patterns: list[re.Pattern] = [
        re.compile(p) if not isinstance(p, re.Pattern) else p for p in patterns
    ]

    match_iterators = [re.finditer(pattern, text) for pattern in comp_patterns]
    matches_list = list(chain.from_iterable(match_iterators))

    matches_list.sort(key=lambda x: x.start(), reverse=reverse)

    for match in matches_list:
        if match:
            yield match
