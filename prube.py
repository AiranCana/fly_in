from generatorData import create_network, Operate, Drones
from pydantic import ValidationError
from excepcions import Parser_error, Movements_errors


prubes = {
    "map/easy/01_linear_path.txt": 1,
    "map/easy/02_simple_fork.txt": 1,
    "map/easy/03_basic_capacity.txt": 1,
    "map/medium/01_dead_end_trap.txt": 1,
    "map/medium/02_circular_loop.txt": 1,
    "map/medium/03_priority_puzzle.txt": 1,
    "map/hard/01_maze_nightmare.txt": 1,
    "map/hard/02_capacity_hell.txt": 1,
    "map/hard/03_ultimate_challenge.txt": 1,
    "map/challenger/01_the_impossible_dream.txt": 45,
}


if __name__ == "__main__":
    try:
        hola = create_network()
        ope: Operate = hola.create_Opertor()
        dron = [Drones(**don.__dict__) for don in ope.drones]
        ope.run(False)
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']}")
    except Parser_error as e:
        print(f"Error: {e}")
    except Movements_errors as e:
        print(e)
