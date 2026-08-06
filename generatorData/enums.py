from strenum import StrEnum


class Zones(StrEnum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Color(StrEnum):
    RED = "\033[38;2;255;0;0m"
    BLUE = "\033[38;2;0;0;255m"
    GREEN = "\033[38;2;0;255;0m"
    CYAN = "\033[38;2;0;255;255m"
    YELLOW = "\033[38;2;255;255;0m"
    MAGENTA = "\033[38;2;255;0;255m"
    PURPLE = "\033[38;2;128;0;128m"
    ORANGE = "\033[38;2;255;165;0m"
    BROWN = "\033[38;2;139;69;19m"
    LIME = "\033[38;2;191;255;0m"
    GOLD = "\033[38;2;255;215;0m"
    BLACK = "\033[38;2;0;0;0m"
    MAROON = "\033[38;2;128;0;0m"
    DARKRED = "\033[38;2;139;0;0m"
    CRIMSON = "\033[38;2;220;20;60m"
    GRAY = "\033[38;2;128;128;128m"
    VIOLET = "\033[38;2;138;43;226m"
    RAINBOW = ""

    RESET = "\033[0m"


RAINBOW = [
    Color.RED,
    Color.ORANGE,
    Color.YELLOW,
    Color.LIME,
    Color.GREEN,
    Color.CYAN,
    Color.BLUE,
    Color.VIOLET,
    Color.PURPLE,
    Color.CRIMSON,
]
