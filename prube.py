"""Quick map regression runner used to validate many maps sequentially.

Runs a set of predefined maps and prints PASS/NO PASS depending on
whether the simulation finishes within the configured number of turns.
"""

from generatorData import create_network, Operate, Drones
from generatorData.enums import Color
from pydantic import ValidationError
from excepcions import Parser_error, Movements_errors
from time import sleep


RED = Color.RED
GREEN = Color.GREEN
RESET = Color.RESET
CYAN = "\033[38;2;0;180;180m"


prubes = {
    "maps/easy/01_linear_path.txt": 6,
    "maps/easy/02_simple_fork.txt": 8,
    "maps/easy/03_basic_capacity.txt": 6,
    "maps/medium/01_dead_end_trap.txt": 12,
    "maps/medium/02_circular_loop.txt": 15,
    "maps/medium/03_priority_puzzle.txt": 12,
    "maps/hard/01_maze_nightmare.txt": 30,
    "maps/hard/02_capacity_hell.txt": 35,
    "maps/hard/03_ultimate_challenge.txt": 45,
    "maps/challenger/01_the_impossible_dream.txt": 45,
}


if __name__ == "__main__":
    try:
        print("Prube of all maps (bonus): ", end="\n\n")
        for maps, total_turns in prubes.items():
            net = create_network(maps)
            ope: Operate = net.create_Opertor()
            dron = [Drones(**don.__dict__) for don in ope.drones]
            turn = ope.run(False)
            if turn > total_turns:
                passed = "NO PASS"
                color = RED
            else:
                passed = "PASS"
                color = GREEN
                print(GREEN, end="")
            print(f"{CYAN}{maps}: {RESET}", end="", flush=True)
            sleep(1.5)
            print(f"{turn}/{total_turns} - ", end="", flush=True)
            sleep(0.5)
            print(f"{color}{passed}{RESET}")
            sleep(0.5)
        print()
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']}")
    except Parser_error as e:
        print(f"Error: {e}")
    except Movements_errors as e:
        print(f"Error: {e}")
