from generatorData import create_network, ValidationError
from drones import Simulation, Drones, Operate
from sys import argv
from excepcions import Parser_error, Movements_errors


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Parser_error("Can found the file")
        hola = create_network(argv[1])
        dron: list[Drones] = hola.create_drones()
        simu: Simulation = hola.create_simulation()
        ope: Operate = hola.create_Opertor()
        move = []
        move.append(dron[0].move_to(hola.start_hub))
        for i in hola.hubs:
            move.append(dron[0].move_to(i))
        move.append(dron[0].move_to(hola.end_hub))
        print(*move, sep=", ")
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']}")
    except Parser_error as e:
        print(f"Error: {e}")
    except Movements_errors as e:
        print(e)
