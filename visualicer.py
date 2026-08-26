"""Command-line wrapper to visualize a network file with pygame.

This module parses the given map file and launches the `visual`
function. It is intended to be executed as a script.
"""

from generatorData import create_network
from pydantic import ValidationError
from sys import argv
from excepcions import Parser_error, Movements_errors
from visual import visual


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Parser_error("The file not cannot be found")
        net = create_network(argv[1])
        name = datas[1].split("/")[-1]
        visual(net, name)
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']}")
    except Parser_error as e:
        print(f"Error: {e}")
    except Movements_errors as e:
        print(f"Error: {e}")
