from generatorData import create_network, Operate
from pydantic import ValidationError
from sys import argv
from excepcions import Parser_error, Movements_errors


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Parser_error("The file not cannot be found")
        net = create_network(argv[1])
        ope: Operate = net.create_Opertor()
        ope.run()
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']}")
    except Parser_error as e:
        print(f"Error: {e}")
    except Movements_errors as e:
        print(f"Error: {e}")
