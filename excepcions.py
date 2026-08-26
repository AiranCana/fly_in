"""Custom exceptions used by the project.

This module defines exceptions raised during parsing and simulation
operations. Each exception preserves a readable message and optional
context information used by command-line tools and visualizers.

"""


class Parser_error(Exception):
    """Raised when the input map/parser encounters invalid format.

    Parameters
    - message: human-readable error message
    - line: optional line number where the error occurred
    - content: optional content of the offending line
    - more: optional additional information to append to the message
    """

    def __init__(self, message: str,
                 line: int | None = None,
                 content: str | None = None,
                 more: str | None = None):
        full_mesage = message
        if line and content:
            full_mesage += f" | line ({line}): {content}"
        if more:
            full_mesage += more
        super().__init__(full_mesage)


class Movements_errors(Exception):
    """Base class for errors raised during drone movement simulation.

    Subclasses represent specific movement-related problems such as
    missing hubs or invalid transitions.
    """


class Found_hub_error(Movements_errors):
    """Raised when a referenced hub cannot be found in the network.

    This exception indicates that a name lookup failed against the
    parsed network data and is used by runtime helpers when a hub is
    expected but not present.

    """
