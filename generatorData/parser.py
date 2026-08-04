from typing import Any, Sequence, Callable
from .genDataZones import Hub, Connection
from pydantic import ValidationError
from excepcions import Parser_error

first: int = 1


class Lecture:
    line: int
    line_valid: int
    line_str: str
    tipe_of_data: str
    datas: list[Any] | str

    def __init__(self, line: int, line_str: str):
        global first
        self.line = line
        self.line_valid = first
        first += 1
        self.line_str = line_str.strip("\n").strip(" ")
        datas = self.line_str.split(": ")
        if (len(datas) != 2 or len(datas[0].strip(" ")) == 0
           or len(datas[1].strip(" ").strip("\n")) == 0):
            raise Parser_error("Bad formate in line",
                               line, line_str.strip("\n"),
                               "\nthe correct formate is "
                               "\"'data_name': 'data'\"")
        self.tipe_of_data = datas[0].strip(" ")
        self.datas = datas[1].strip(" ").strip("\n")


def __optendata_hub(lecture: Lecture) -> dict[str, Any]:
    lis = ["zone", "color", "max_drones"]
    sol: dict[str, Any] = {}
    sol.update({"name": lecture.datas[0]})
    sol.update({"x": lecture.datas[1]})
    sol.update({"y": lecture.datas[2]})
    for i in lecture.datas[3:]:
        n = i.split("=")
        if len(n) != 2:
            raise Parser_error("Bad sintaxix in hubs in metadata",
                               lecture.line, lecture.line_str)
        if not (n[0] in lis):
            raise Parser_error("Bad sintaxix in hubs in metadata",
                               lecture.line, lecture.line_str,
                               f"\nOnly need this metadata {lis}")
        sol.update({n[0]: n[1]})
    return sol


def __opten_connection(lecture: Lecture) -> dict[str, str]:
    sol: dict[str, Any] = {}
    hubs = lecture.datas[0].split("-")
    if len(hubs) != 2:
        raise Parser_error("Bad syntax in 'connection'",
                           lecture.line, lecture.line_str,
                           ("\nthe correct formate is "
                            "\"'connection': 'name_hub'-'name_hub'\""))
    sol.update({"name_first_hub": hubs[0]})
    sol.update({"name_second_hub": hubs[-1]})
    if lecture.datas[-1].startswith("["):
        sol = __get_metadata(lecture.datas, lecture, sol)
    elif lecture.datas[-1].endswith("]"):
        if lecture.datas[-1] != "]":
            raise Parser_error("Bad syntax in metadato of 'connection' ",
                               lecture.line, lecture.line_str,
                               ("\nthe meatadata only have 1 thing: "
                                "'max_link_capacity'"))
        else:
            raise Parser_error("Bad syntax",
                               lecture.line, lecture.line_str)
    return sol


def __get_metadata(datas: Sequence[str],
                   lecture: Lecture,
                   sol: dict[str, str]) -> dict[str, str]:
    lis = "max_link_capacity"
    metadata = datas[-1].strip("[").strip("]").split(" ")
    for i in metadata:
        data = i.split("=")
        if len(data) != 2:
            raise Parser_error("Bad sintaxix in hubs in metadata",
                               lecture.line, lecture.line_str)
        if data[0] != lis:
            raise Parser_error("Bad sintaxix in hubs in metadata",
                               lecture.line, lecture.line_str,
                               f"\nOnly need this metadata '{lis}'")
        sol.update({data[0]: data[-1]})
    return sol


def __prubes(prube: dict[str, str], lines: Lecture, prub: Any) -> None:
    try:
        prub.model_validate(prube.copy())
    except ValidationError as e:
        mensgges = [
            err["msg"].replace("Value error, ", "") for err in e.errors()
            ]
        text = "Value error: ".join(mensgges)
        raise Parser_error(f"{text}", lines.line, lines.line_str)
    except Exception as e:
        raise Parser_error(f"{e}", lines.line, lines.line_str)


def __optend_data(ope: Callable[..., Any], lines: Lecture) -> Any:
    try:
        prube = ope(lines)
    except ValueError as e:
        raise Parser_error(f"{e}", lines.line, lines.line_str,
                           ("\n the correct format of metadata is "
                            "\"'name'='value'\""))
    return prube


def __generate_datas_line(lines: Lecture, sol: dict[str, Any],
                          connect: list[dict[str, str]],
                          hubs: list[dict[str, str]]
                          ) -> tuple[dict[str, Any], list[dict[str, str]],
                                     list[dict[str, str]]]:
    if lines.line_valid == 1 and lines.tipe_of_data != "nb_drones":
        raise Parser_error("Need start with 'nb_drones'",
                           lines.line, lines.line_str)
    elif lines.line_valid == 1:
        sol.update({lines.tipe_of_data: lines.datas})
    else:
        if not (lines.tipe_of_data.find("hub") + 1):
            if isinstance(lines.datas, str):
                lines.datas = lines.datas.split(" ")
            prube: dict[str, Any] = __optend_data(__opten_connection, lines)
            __prubes(prube, lines, Connection)
            connect.append(prube)
        else:
            if isinstance(lines.datas, str):
                lines.datas = lines.datas.replace("]", "").replace("[", "")
                lines.datas = lines.datas.split(" ")
            if len(lines.datas) < 3:
                raise Parser_error("Bad formate in line", lines.line,
                                   lines.line_str,
                                   ("\nthe correct formate is "
                                    "\"\t'data_name': 'data'\"\n"
                                    "\"\t'data_name': 'data'\""))
            prube = __optend_data(__optendata_hub, lines)
            __prubes(prube, lines, Hub)
            if lines.tipe_of_data == "hub":
                hubs.append(prube)
            else:
                sol.update({lines.tipe_of_data: prube})
    return (sol, connect, hubs)


def _lecture(file: str) -> dict[str, Any]:
    global first
    first = 1
    sol: dict[str, Any] = {}
    connect: list[dict[str, str]] = []
    hubs: list[dict[str, str]] = []
    with open(file) as fd:
        for line, content in enumerate(fd.readlines(), start=1):
            if not content.startswith("#") and content != "\n":
                lines = Lecture(line, content)
            else:
                lines = None
            if lines:
                sol, connect, hubs = __generate_datas_line(
                    lines,
                    sol,
                    connect,
                    hubs
                )
    sol.update({"connections": connect})
    sol.update({"hubs": hubs})
    return sol
