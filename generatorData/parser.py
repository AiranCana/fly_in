from typing import Any, Sequence
from excepcions import Parser_error


def __optendata_hub(lecture: Sequence[str]) -> dict[str, Any]:
    sol: dict[str, Any] = {}
    sol.update({"name": lecture[0]})
    sol.update({"x": lecture[1]})
    sol.update({"y": lecture[2]})
    for i in lecture[3:]:
        n = i.split("=")
        if len(n) != 2:
            raise Parser_error("Bad sintaxix in hubs")
        sol.update({n[0]: n[1]})
    return sol


def __opten_hub(lecture: list[Any] | Sequence[str],
               singular: bool = True) -> dict[str, str] | list[dict[str, str]]:
    lis = []
    if singular:
        return __optendata_hub(lecture)
    lis = [__optendata_hub(x) for x in lecture]
    return lis


def __opten_connection(lecture: Sequence[str]) -> dict[str, str]:
    sol: dict[str, Any] = {}
    hubs = lecture[0].split("-")
    if len(hubs) != 2:
        raise Parser_error("Bad sintaxis in 'connection'")
    sol.update({"name_first_hub": hubs[0]})
    sol.update({"name_second_hub": hubs[-1]})
    if lecture[-1].startswith("["):
        sol = __get_metadata(lecture, sol)
    return sol


def __get_metadata(lecture: Sequence[str],
                   sol: dict[str, str]) -> dict[str, str]:
    metadata = lecture[-1].strip("[").strip("]").split(" ")
    for i in metadata:
        data = i.split("=")
        if len(data) != 2:
            raise Parser_error("Bad sintaxis")
        sol.update({data[0]: data[-1]})
    return sol


def __found_hub(lecture: list[list[str]]) -> dict[str, Any]:
    sol: dict[str, Any] = {}
    found = [x for x in lecture if x[0] == "hub"]
    start = [x for x in lecture if x[0] == "start_hub"]
    end = [x for x in lecture if x[0] == "end_hub"]
    found_clean = [[x[0], x[1].replace("[", "").replace("]", "").split(" ")]
                   for x in found]
    start_clean = [
        [x[0], x[1].replace("[", "").replace("]", "").split(" ")]
        for x in start]
    end_clean = [
        [x[0], x[1].replace("[", "").replace("]", "").split(" ")]
        for x in end]
    if (len(start_clean) != 1 or
       len(start_clean[0]) != 2 or
       len(start_clean[0][1]) < 3):
        raise Parser_error("Bad sintaxix in 'start_hub'")
    if (len(end_clean) != 1 or
       len(end_clean[0]) != 2 or
       len(end_clean[0][1]) < 3):
        raise Parser_error("Bad sintaxix in 'end_hub'")
    for i in found_clean:
        if len(i) != 2 or len(i[1]) < 3:
            raise Parser_error("Bad sintaxix in 'hub'")
    found_filtre = [x[1] for x in found_clean]
    sol.update({"start_hub": __opten_hub(start_clean[0][1])})
    sol.update({"end_hub": __opten_hub(end_clean[0][1])})
    sol.update({"hubs": __opten_hub(found_filtre, False)})
    return sol


def __found_connection(lecture: list[list[str]]) -> dict[str, Any]:
    sol: dict[str, Any] = {}
    lis: list[dict[str, Any]] = []
    found: list[list[str]] = [x for x in lecture if x[0] == "connection"]
    found2 = [[x[0], x[1].split(" ")] for x in found]
    for i in found2:
        if len(i) != 2:
            raise Parser_error(f"Bad sintaxix in 'connection' = {i}")
    lis = [__opten_connection(i[1]) for i in found2]
    sol.update({"connections": lis})
    return sol


def _lecture(file: str) -> dict[str, Any]:
    lecture: list[list[str]] = []
    sol: dict[str, str] = {}

    with open(file) as fd:
        for line in fd.readlines():
            if not line.startswith("#") and line != "\n":
                lecture.append(line.strip(" ").strip("\n").split(": "))
    if not lecture[0][0].startswith("nb_drones"):
        raise Parser_error("Need start with 'nb_drones'")
    sol.update({lecture[0][0]: lecture[0][1]})
    lecture = lecture[1:]
    sol.update(__found_hub(lecture))
    sol.update(__found_connection(lecture))
    return sol
