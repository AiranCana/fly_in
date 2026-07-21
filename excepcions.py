class Parser_error(Exception):

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
