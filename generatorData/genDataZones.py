"""Data models representing hubs, connections and network configuration.

This module defines Pydantic models used to represent the network graph
of hubs and connections and helpers to build runtime factories used by
the simulation and operator layers.
"""

from pydantic import BaseModel, Field, ValidationError, model_validator
from .enums import Zones, Color
from typing import Any, overload


class Hub (BaseModel):
    """Immutable model describing a single hub/node in the network.

    Attributes
    - x, y: grid coordinates of the hub
    - zone: zone type (normal, blocked, restricted, priority)
    - color: optional terminal color code used for pretty printing
    - max_drones: maximum simultaneous drones that can occupy the hub
    - name: unique hub name
    """

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
        """Pre-validate and coerce input mapping for `Hub` construction.

        Parameters
        - data: raw string-valued mapping parsed from the map file

        Returns
        - dict[str, Any]: coerced mapping suitable for Pydantic model parsing
        """
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
            raise ValidationError("Max 'drones' or 'x' or 'y' is invalid")
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
    """Immutable model describing a connection/link between two hubs.

    Attributes
    - max_link_capacity: maximum concurrent drones allowed on the link
    - name_first_hub, name_second_hub: names of the connected hubs
    """

    model_config = {"frozen": True}

    max_link_capacity: int = Field(ge=1, default=1)
    name_first_hub: str = Field(min_length=1)
    name_second_hub: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        """Coerce connection metadata types prior to model validation.

        Parameters
        - data: raw mapping for a Connection

        Returns
        - dict[str, Any]: mapping with converted numeric fields when present
        """
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
        """Post-validate that the connection links two distinct hubs.

        Raises
        - ValueError: when both endpoint names are equal
        """
        if self.name_first_hub == self.name_second_hub:
            raise ValueError("The hubs can't be the same")
        return self


class NetworkFly(BaseModel):
    """Top-level model representing the entire drone network.

    Contains hubs, connections and the configured number of drones.
    Provides helper factories used by the runtime to create simulations
    and operators.
    """

    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    connections: list[Connection]
    nb_drones: int = Field(ge=1)
    hub_by_name: dict[str, Hub] = {}

    @model_validator(mode="before")
    @classmethod
    def parser(self, data: dict[str, str]) -> dict[str, Any]:
        """Coerce top-level `NetworkFly` input mapping before model parsing.

        Parameters
        - data: raw mapping parsed from the map file

        Returns
        - dict[str, Any]: mapping with numeric conversions applied
        """
        sol: dict[str, Any] = data
        try:
            nb_drones = data["nb_drones"]
            sol.update({"nb_drones": int(nb_drones)})
            return sol
        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Max drones invalid")

    @model_validator(mode="after")
    def validator(self) -> "NetworkFly":
        """Post-validate `NetworkFly` invariants and build helper dict.

        Checks for duplicate hubs/connections and initializes the
        `hub_by_name` lookup used by runtime helpers.
        """
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
            if not (self.found_first_hub(i) and self.found_first_hub(i)):
                raise ValueError("Not found this conection "
                                 f"{i.name_first_hub} - {i.name_second_hub}")
        prube_name_hub = {i.name for i in prubeh}
        if len(prube_name_hub) != len(prubeh):
            raise ValueError("There are duplicates hubs")
        self.__generate_dict()
        return self

    def __generate_dict(self) -> None:
        """Populate the `hub_by_name` mapping from model hub objects.

        This helper creates a name->Hub dictionary including start and
        end hubs for fast runtime lookups.
        """
        sol: dict[str, Hub] = {}
        sol.update({self.start_hub.name: self.start_hub})
        sol.update({self.end_hub.name: self.end_hub})
        for hub in self.hubs:
            sol.update({hub.name: hub})
        self.hub_by_name.update(sol)

    @overload
    def found_hub(self, con_name: Connection) -> Hub | None:
        ...

    @overload
    def found_hub(self, con_name: str) -> Hub | None:
        ...

    def found_hub(self, con_name: Connection | str) -> Hub | None:
        """Return a `Hub` by connection object or by hub name.

        Parameters
        - con_name: either a `Connection` (returns the second hub) or a
          string hub name (lookup via `hub_by_name`).

        Returns
        - Hub | None: found hub instance or `None` if not present
        """
        if isinstance(con_name, Connection):
            next_hub = con_name.name_second_hub
            for i in self.hubs:
                if i.name == next_hub:
                    return i
            if self.start_hub.name == next_hub:
                return self.start_hub
            if self.end_hub.name == next_hub:
                return self.end_hub
            return None
        return self.hub_by_name.get(con_name, None)

    def found_first_hub(self, connect: Connection) -> Hub | None:
        """Return the `Hub` corresponding to the first endpoint name.

        Parameters
        - connect: connection object whose first endpoint will be resolved

        Returns
        - Hub | None: resolved hub or `None` if not found
        """
        next_hub = connect.name_first_hub
        return self.__found_hub(next_hub)

    def found_second_hub(self, connect: Connection) -> Hub | None:
        """Return the `Hub` corresponding to the second endpoint name.

        Parameters
        - connect: connection object whose second endpoint will be resolved

        Returns
        - Hub | None: resolved hub or `None` if not found
        """
        next_hub = connect.name_second_hub
        return self.__found_hub(next_hub)

    def __found_hub(self, next_hub: str) -> Hub | None:
        """Resolve a hub by name among hubs, start and end.

        Returns `None` when no hub with `next_hub` name exists.
        """
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
        """Find connections touching a hub or the specific connection.

        Parameters
        - hub_f: either a `Hub` (returns list of `Connection`) or a
          frozenset of two hub names (returns the `Connection` or `None`).

        Returns
        - list[Connection] | Connection | None
        """
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
        """Create runtime `Drones` instances using `factory_drones`.

        Returns
        - list[Any]: list of created drone objects
        """
        return self.factory_drones(
            self.nb_drones,
            self.start_hub,
            self.end_hub
        )

    def __create_simulation(self) -> Any:
        """Create a `Simulation` instance via `factory_simulation`.

        Returns
        - Any: runtime simulation object
        """
        return self.factory_simulation()

    def create_Opertor(self) -> Any:
        """Convenience factory: create `Simulation`, drones and `Operate`.

        Returns
        - Any: an `Operate` instance ready to run the simulation
        """
        sim = self.__create_simulation()
        lis = self.__create_drones()
        return self.factory_operate(lis, sim)

    def factory_drones(self, number: int, start: Hub, end: Hub) -> list[Any]:
        """Factory to instantiate drone objects for runtime.

        Parameters
        - number: number of drones to create
        - start, end: start and end `Hub` instances

        Returns
        - list[Any]: created drone instances
        """
        from generatorData.operations.drones import Drones
        x = [Drones(i + 1, start, end) for i in range(number)]
        return x

    def factory_simulation(self) -> Any:
        """Factory to create a `Simulation` instance for this network.

        Returns
        - Any: a `Simulation` object
        """
        from generatorData.operations.simulation import Simulation
        return Simulation(self)

    def factory_operate(self, lis: list[Any], simu: Any) -> Any:
        """Factory to create an `Operate` controller from drones and sim.

        Parameters
        - lis: list of drone instances
        - simu: simulation instance

        Returns
        - Any: an `Operate` controller
        """
        from generatorData.operations.operation import Operate
        return Operate(lis, simu)


def create_network(file: str) -> "NetworkFly":
    """Load and validate a network definition from `file`.

    Parameters
    - file: path to the map definition file

    Returns
    - NetworkFly: validated network model ready for simulation

    Raises
    - Parser_error: for parsing errors in the input file
    - pydantic.ValidationError: when the parsed data fails model
      validation
    """
    from generatorData.parser import _lecture
    sol: dict[str, Any] = _lecture(file)
    return NetworkFly.model_validate(sol)
