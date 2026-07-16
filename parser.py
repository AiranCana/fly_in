from pydantic import BaseModel, Field, ValidationError, model_validator
from strenum import StrEnum
from dataclasses import dataclass
from sys import argv
from typing import Any
import json


class PrintableModel(BaseModel):
    """Base con serialización a dict/JSON, separando campos con
    valor por defecto en un apartado 'metadata'."""

    def to_dict(self) -> dict[str, Any]:
        core: dict[str, Any] = {}
        metadata: dict[str, Any] = {}

        for field_name, field_info in type(self).model_fields.items():
            value = getattr(self, field_name)
            value = self._serialize_value(value)

            if field_info.is_required():
                core[field_name] = value
            else:
                metadata[field_name] = value

        if metadata:
            core["metadata"] = metadata
        return core

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, PrintableModel):
            return value.to_dict()
        if isinstance(value, list):
            return [PrintableModel._serialize_value(v) for v in value]
        if isinstance(value, StrEnum):
            return value.name.lower()
        return value

    def printer(self) -> None:
        print(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))

class Zones(StrEnum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Color(StrEnum):
    RED = "\033[38;2;255;0;0m"
    BLUE = "\033[38;2;0;0;255m"
    GREEN = "\033[38;2;0;255;0m"
    CYAN = "\033[38;2;0;255;255m"
    YELLOW = "\033[38;2;255;255;0m"
    MAGENTA = "\033[38;2;255;0;255m"
    PURPLE = "\033[38;2;128;0;128m"
    ORANGE = "\033[38;2;255;165;0m"
    BROWN = "\033[38;2;139;69;19m"
    LIME = "\033[38;2;191;255;0m"
    GOLD = "\033[38;2;255;215;0m"
    BLACK = "\033[38;2;0;0;0m"
    MAROON = "\033[38;2;128;0;0m"
    DARKRED = "\033[38;2;139;0;0m"
    CRIMSON = "\033[38;2;220;20;60m"
    RAINBOW = ""

    RESET = "\033[0m"


@dataclass(slots=True)
class Hub (PrintableModel):
    model_config = {"frozen": True}

    zone: Zones = Field(default=Zones.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1)
    name: str = Field(min_length=3)
    x: int = Field()
    y: int = Field()

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        sol: dict[str, Any] = data

        try:
            x = data["x"]
            y = data["y"]
            sol.update({"y": int(y)})
            sol.update({"x": int(x)})
            zone: Zones = Zones.NORMAL
            zon = data.get("zone", None)
            match zon:
                case Zones.NORMAL:
                    zone = Zones.NORMAL
                case Zones.BLOCKED:
                    zone = Zones.BLOCKED
                case Zones.RESTRICTED:
                    zone = Zones.RESTRICTED
                case Zones.PRIORITY:
                    zone = Zones.PRIORITY
                case None:
                    pass
                case _:
                    raise ValidationError("Zone not valid")
            color: Color = Color.RED
            col = data.get("color", None)
            match col:
                case "red":
                    color = Color.RED
                case "blue":
                    color = Color.BLUE
                case "green":
                    color = Color.GREEN
                case "cyan":
                    color = Color.CYAN
                case "yellow":
                    color = Color.YELLOW
                case "magenta":
                    color = Color.MAGENTA
                case "purple":
                    color = Color.PURPLE
                case "orange":
                    color = Color.ORANGE
                case "brown":
                    color = Color.BROWN
                case "lime":
                    color = Color.LIME
                case "gold":
                    color = Color.GOLD
                case "black":
                    color = Color.BLACK
                case "maroon":
                    color = Color.MAROON
                case "darkred":
                    color = Color.DARKRED
                case "crimson":
                    color = Color.CRIMSON
                case "rainbow":
                    color = Color.RAINBOW
                case None:
                    pass
                case _:
                    raise ValidationError("Color not valid")
            max_drones = data.get("max_drones", None)
            if max_drones:
                sol.update({"max_drones": int(max_drones)})
            sol.update({"zone": zone})
            sol.update({"color": color})
            return sol
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")


@dataclass(slots=True)
class Connection(PrintableModel):
    model_config = {"frozen": True}

    max_link_capacity: int = Field(ge=1, default=1)
    nameFirstHub: str = Field(min_length=3)
    nameSecondHub: str = Field(min_length=3)

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        sol: dict[str, Any] = data
        try:
            max_link_capacity = data.get("max_link_capacity", None)
            if max_link_capacity:
                sol.update({"max_link_capacity": int(max_link_capacity)})
            return sol
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")

    @model_validator(mode="after")
    def validator(self) -> "Connection":
        assert self.nameFirstHub != self.nameSecondHub, ("The hubs can't be"
                                                         " the same")
        return self


@dataclass(slots=True)
class NetworkFly(PrintableModel):

    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    connections: list[Connection]
    nb_drones: int = Field(ge=1)

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        sol: dict[str, Any] = data
        try:
            nb_drones = data["nb_drones"]
            sol.update({"nb_drones": int(nb_drones)})
            return sol
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")

    @model_validator(mode="after")
    def validator(self) -> "NetworkFly":
        prubeh: list[Hub] = self.hubs
        prubec: list[Connection] = self.connections
        prubeh.append(self.start_hub)
        prubeh.append(self.end_hub)
        assert len(prubeh) == len(set(prubeh)), ("There are duplicates hubs")
        assert len(prubec) == len(set(prubec)), ("There are duplicates"
                                                 " connections")
        return self


def __optendataHub(lecture: list[str]) -> dict[str, Any]:
    sol: dict[str, Any] = {}
    sol.update({"name": lecture[0]})
    sol.update({"x": lecture[1]})
    sol.update({"y": lecture[2]})
    for i in lecture[3:]:
        i = i.split("=")
        assert len(i) == 2, "Bad sintaxix in hubs"
        sol.update({i[0]: i[1]})
    return sol


def optenHub(lecture: list[Any],
             singular: bool = True) -> dict[str, str] | list[dict[str, str]]:
    lis: list[dict[str, str]] = []
    if singular:
        return __optendataHub(lecture)
    lis = [__optendataHub(x) for x in lecture]
    return lis


def __optenConnection(lecture: list[Any]) -> dict[str, str]:
    sol: dict[str, str] = {}
    hubs = lecture[0].split("-")
    assert len(hubs) == 2, "Bad sintaxis in 'connection'"
    sol.update({"nameFirstHub": hubs[0]})
    sol.update({"nameSecondHub": hubs[-1]})
    if lecture[-1].startswith("["):
        sol = __get_metadata(lecture, sol)
    return sol


def __get_metadata(lecture: list[str], sol: dict[str, str]) -> dict[str, str]:
    metadata = lecture[-1].strip("[").strip("]").split(" ")
    for i in metadata:
        data = i.split("=")
        assert len(data) == 2, "Bad sintaxis"
        sol.update({data[0]: data[-1]})
    return sol


def __foundHub(lecture: list[list[str]]) -> dict[str, Any]:
    sol: dict[str, str] = {}
    foun: list[list[str]] = [x for x in lecture if x[0] == "hub"]
    start: list[list[str]] = [x for x in lecture if x[0] == "start_hub"]
    end: list[list[str]] = [x for x in lecture if x[0] == "end_hub"]
    foun = [[x[0], x[1].replace("[", "").replace("]", "").split(" ")]
            for x in foun]
    start = [[x[0], x[1].replace("[", "").replace("]", "").split(" ")]
             for x in start][0]
    end = [[x[0], x[1].replace("[", "").replace("]", "").split(" ")]
           for x in end][0]
    assert len(start) == 2 and len(start[1]) >= 3, ("Bad sintaxix in "
                                                    "'start_hub'")
    assert len(end) == 2 and len(end[1]) >= 3, "Bad sintaxix in 'end_hub'"
    for i in foun:
        assert len(i) == 2 and len(i[1]) >= 3, "Bad sintaxix in 'hub'"
    foun = [x[1] for x in foun]
    sol.update({"start_hub": optenHub(start[1])})
    sol.update({"end_hub": optenHub(end[1])})
    sol.update({"hubs": optenHub(foun, False)})
    return sol


def __foundConnection(lecture: list[list[str]]) -> dict[str, Any]:
    sol: dict[str, Any] = {}
    lis: list[dict[str, Any]] = []
    foun: list[list[str]] = [x for x in lecture if x[0] == "connection"]
    foun = [[x[0], x[1].split(" ")] for x in foun]
    for i in foun:
        assert len(i) == 2, f"Bad sintaxix in 'connection' = {i}"
    lis = [__optenConnection(i[1]) for i in foun]
    sol.update({"connections": lis})
    return sol


def __lecture(file: str) -> dict[str, Any]:
    lecture: list[list[str]] = []
    sol: dict[str, str] = {}

    with open(file) as fd:
        for line in fd.readlines():
            if not line.startswith("#") and line != "\n":
                lecture.append(line.strip(" ").strip("\n").split(": "))
    assert lecture[0][0].startswith("nb_drones"), "Need start with 'nb_drones'"
    sol.update({lecture[0][0]: lecture[0][1]})
    lecture = lecture[1:]
    sol.update(__foundHub(lecture))
    sol.update(__foundConnection(lecture))
    return sol


def createNetwork(file: str) -> "NetworkFly":
    sol: dict[str, str] = __lecture(file)
    # for i, v in sol.items():
    #    print(f"{i} - {v}")
    return NetworkFly.model_validate(sol)


if __name__ == "__main__":
    try:
        hola = createNetwork(argv[1])
        hola.printer()
    except Exception as e:
        print(e)
