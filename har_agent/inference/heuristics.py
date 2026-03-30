from __future__ import annotations

import math
import re
from collections import Counter

from har_agent.models.findings import ValueHeuristic


UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
HEX_HASH_LENGTHS = {32, 40, 64, 128}


def detect_value_heuristics(value: str | None) -> list[ValueHeuristic]:
    if value is None:
        return []

    results: list[ValueHeuristic] = []
    if UUID_RE.match(value):
        results.append(ValueHeuristic(type="uuid", confidence="high", rationale="Value matches UUID shape."))

    if value.isdigit() and len(value) in {10, 13}:
        results.append(
            ValueHeuristic(
                type="timestamp",
                confidence="medium",
                rationale="Numeric value length matches common Unix timestamp formats.",
            )
        )

    entropy = shannon_entropy(value)
    if len(value) >= 12 and entropy >= 3.5:
        results.append(
            ValueHeuristic(
                type="random_like",
                confidence="low",
                rationale="Value length and entropy suggest a random-looking token.",
            )
        )

    if all(character in "0123456789abcdefABCDEF" for character in value) and len(value) in HEX_HASH_LENGTHS:
        results.append(
            ValueHeuristic(
                type="hash_like",
                confidence="medium",
                rationale="Value length and alphabet match common hex hash digests.",
            )
        )
    return results


def shannon_entropy(value: str) -> float:
    counts = Counter(value)
    length = len(value)
    if length == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy
