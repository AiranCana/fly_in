from generatorData import create_network, ValidationError
from sys import argv


if __name__ == "__main__":
    try:
        datas = argv
        if len(argv) != 2:
            raise Exception("Can found the file")
        hola = create_network(argv[1])
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error["msg"]}")
    except Exception as e:
        print(f"Error: {e}")
