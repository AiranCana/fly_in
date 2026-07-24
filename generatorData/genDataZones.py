from pydantic import BaseModel, Field, ValidationError, model_validator
from strenum import StrEnum
from typing import Any, overload


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
    GRAY = "\033[38;2;128;128;128m"
    VIOLET = "\033[38;2;138;43;226m"
    RAINBOW = ""

    RESET = "\033[0m"


RAINBOW = [
    Color.RED,
    Color.ORANGE,
    Color.YELLOW,
    Color.LIME,
    Color.GREEN,
    Color.CYAN,
    Color.BLUE,
    Color.VIOLET,
    Color.PURPLE,
    Color.CRIMSON,
]


class Hub (BaseModel):
    model_config = {"frozen": True}

    x: int
    y: int
    zone: Zones = Field(default=Zones.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1)
    name: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        sol: dict[str, Any] = data
        try:
            x = data["x"]
            y = data["y"]
            max_drones = data.get("max_drones", None)
            if max_drones:
                sol.update({"max_drones": int(max_drones)})
            sol.update({"y": int(y)})
            sol.update({"x": int(x)})
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max 'drones' or 'x' or 'y' invalid")
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
                raise ValueError("Zone not valid")
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
            case "gray":
                color = Color.GRAY
            case "rainbow":
                color = Color.RAINBOW
            case "violet":
                color = Color.VIOLET
            case None:
                pass
            case _:
                raise ValueError("Color not valid")
        sol.update({"zone": zone})
        sol.update({"color": color})
        return sol


class Connection(BaseModel):
    model_config = {"frozen": True}

    max_link_capacity: int = Field(ge=1, default=1)
    name_first_hub: str = Field(min_length=1)
    name_second_hub: str = Field(min_length=1)

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
        if self.name_first_hub == self.name_second_hub:
            raise ValueError("The hubs can't be the same")
        return self


class NetworkFly(BaseModel):

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
        prubeh: list[Hub] = self.hubs.copy()
        prubec: list[Connection] = self.connections.copy()
        prubeh.append(self.start_hub)
        prubeh.append(self.end_hub)
        prubec_pairs = {frozenset((x.name_first_hub,
                                   x.name_second_hub)) for x in prubec}
        if len(prubeh) != len(set(prubeh)):
            raise ValueError("There are duplicates hubs")
        if len(prubec) != len(prubec_pairs):
            raise ValueError("There are duplicates connections")
        for i in prubec:
            if not (self.found_hub(i) and self.found_first_hub(i)):
                raise ValueError("not found this conection "
                                 f"{i.name_first_hub} - {i.name_second_hub}")
        prube_name_hub = {i.name for i in prubeh}
        if len(prube_name_hub) != len(prubeh):
            raise ValueError("There are duplicates hubs")
        return self

    def found_hub(self, connect: Connection) -> Hub | None:
        next_hub = connect.name_second_hub
        for i in self.hubs:
            if i.name == next_hub:
                return i
        if self.start_hub.name == next_hub:
            return self.start_hub
        if self.end_hub.name == next_hub:
            return self.end_hub
        return None

    def found_first_hub(self, connect: Connection) -> Hub | None:
        next_hub = connect.name_first_hub
        return self.__found_hub(next_hub)

    def found_second_hub(self, connect: Connection) -> Hub | None:
        next_hub = connect.name_second_hub
        return self.__found_hub(next_hub)

    def __found_hub(self, next_hub: str) -> Hub | None:
        for i in self.hubs:
            if i.name == next_hub:
                return i
        if self.start_hub.name == next_hub:
            return self.start_hub
        if self.end_hub.name == next_hub:
            return self.end_hub
        return None

    @overload
    def found_connects(self, hub_f: Hub) -> list[Connection]:
        ...

    @overload
    def found_connects(self, hub_f: frozenset[str]) -> Connection | None:
        ...

    def found_connects(self,
                       hub_f: Hub | frozenset[str]
                       ) -> list[Connection] | Connection | None:
        if isinstance(hub_f, Hub):
            connect: list[Connection] = []
            hub_f_name = hub_f.name
            for i in self.connections:
                if (hub_f_name in (i.name_first_hub, i.name_second_hub)):
                    connect.append(i)
            return connect
        for i in self.connections:
            if frozenset((i.name_first_hub, i.name_second_hub)) == hub_f:
                return i
        return None

    def __create_drones(self) -> list[Any]:
        from factory import factory_drones
        return factory_drones(
            self.nb_drones,
            self.start_hub,
            self.end_hub
        )

    def __create_simulation(self) -> Any:
        from factory import factory_simulation
        return factory_simulation(self)

    def create_Opertor(self) -> Any:
        from factory import factory_operate
        sim = self.__create_simulation()
        lis = self.__create_drones()
        return factory_operate(lis, sim)


def create_network(file: str) -> "NetworkFly":
    from generatorData.parser import _lecture
    sol: dict[str, str] = _lecture(file)
    return NetworkFly.model_validate(sol)
