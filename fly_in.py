from generatorData import create_network, ValidationError
from sys import argv
from excepcions import Parser_error


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Parser_error("Can found the file")
        hola = create_network(argv[1])
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error["msg"]}")
            print(e)
    except Parser_error as e:
        print(f"Error: {e}")
