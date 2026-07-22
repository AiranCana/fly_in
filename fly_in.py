from generatorData import create_network, ValidationError
from drones import Simulation, Drones
from sys import argv
from excepcions import Parser_error


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Parser_error("Can found the file")
        hola = create_network(argv[1])
        dron: list[Drones] = hola.create_drones()
        simu: Simulation = hola.create_simulation()
        print(simu.zone_count)
        print(*simu.connect_count, sep="\n")
        dron[0].move_to(hola.start_hub, simu)
        print(", ", end="")
        for i in hola.hubs:
            dron[0].move_to(i, simu)
            print(", ", end="")
        dron[0].move_to(hola.end_hub, simu)
        print()
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error["msg"]}")
    except Parser_error as e:
        print(f"Error: {e}")
