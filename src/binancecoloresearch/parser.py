"""
Parser module for extracting Binance URL constants from configuration files.
"""

import re
from pathlib import Path
from typing import TypedDict, Union


class EndpointConstant(TypedDict):
    """Type definition for an endpoint constant."""

    constant: str
    category: str
    domain: str


def parse_constants(filepath: Union[str, Path]) -> list[EndpointConstant]:
    """
    Parse Binance endpoint constants from a text file.

    The file format is:
    # Category Name
    CONSTANT_NAME = "https://domain.com"

    Args:
        filepath: Path to the file containing URL constants

    Returns:
        List of dictionaries containing constant name, category, and domain
    """
    constants: list[EndpointConstant] = []
    category = None
    pattern = re.compile(r'(\w+)\s*=\s*"(https?://|wss://)([^"/]+)')

    with Path(filepath).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                category = line[1:].strip()
            elif match := pattern.search(line):
                constants.append(
                    {
                        "constant": match.group(1),
                        "category": category or "Unknown",
                        "domain": match.group(3),
                    }
                )

    return constants
