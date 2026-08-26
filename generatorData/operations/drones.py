"""Drone representation and printing utilities.

Defines the `Drones` dataclass which holds a drone's state and
methods to progress along its assigned route and produce printable
status messages.
"""

from typing import Optional
from generatorData import Hub, NetworkFly, Connection
from generatorData.enums import RAINBOW, Color
from random import randint
from dataclasses import dataclass
from excepcions import Found_hub_error


@dataclass
class Drones:
    """Mutable dataclass storing a single drone's runtime state.

    Attributes
    - id: drone identifier
    - hub: current hub where the drone is located
    - end_hub: destination hub
    - move: whether the drone is currently moving
    - torns_sleep: waiting turns counter
    - in_air: whether the drone is currently in transit on a link
    - route: optional assigned route (list of Hub excluding current hub)
    - route_pos: index into the route for the next target
    """

    id: int
    hub: Hub
    end_hub: Hub
    move: bool = False
    torns_sleep: int = 0
    in_air: bool = False
    route: Optional[list[Hub]] = None
    route_pos: int = 0

    def moves(self) -> str:
        """Advance the drone one step along its route.

        Returns
        - str: human-readable short status describing the new position
          (e.g., "D1-HubName").
        """
        if not self.move:
            self.move = True
        self.hub = self.get_hub_route()
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.in_air = False
        self.route_pos += 1
        return self.__printer()

    def wait(self, net: NetworkFly | None = None) -> str | None:
        """Increment wait counter and return a printable status.

        Parameters
        - net: optional `NetworkFly` used to include connection details

        Returns
        - str | None: printable status string when the drone is moving or
          a connection description when `net` is provided; otherwise
          `None`.
        """
        self.torns_sleep += 1
        if not self.in_air and self.move:
            return self.__printer()
        if net is not None:
            return self.__printer_connection(net)
        return None

    def __printer(self) -> str:
        """Return the drone's short printable status.

        Returns
        - str: formatted status prefixed with the drone id (e.g. "D1-HubName"),
          using hub color formatting (rainbow or fixed color).
        """
        text = f"{self.hub.name}"
        sol = ""
        if self.hub.color != Color.RAINBOW:
            sol = self.__print_hub(text, self.hub)
            sol = f"D{self.id}-" + sol
            return sol
        sol = self.__print_hub_rainbow(text)
        sol = f"D{self.id}-" + sol
        return sol

    def __print_hub(self, text: str, hub: Hub) -> str:
        """Wrap the given `text` with the hub's color and reset code.

        Parameters
        - text: the text to colorize
        - hub: the `Hub` providing color information

        Returns
        - str: colored text followed by `Color.RESET`.
        """
        sol = ""
        if isinstance(hub.color, str):
            sol += hub.color
        sol += text
        sol += Color.RESET
        return sol

    def __print_hub_rainbow(self, text: str) -> str:
        """Apply a repeating rainbow color sequence to `text`.

        The sequence starts at a random offset into `RAINBOW` so adjacent
        calls can differ visually.

        Parameters
        - text: input text to colorize

        Returns
        - str: rainbow-colored text followed by `Color.RESET`.
        """
        sol = ""
        longi = len(RAINBOW)
        start = randint(0, longi)
        for i in text:
            sol += RAINBOW[start % longi]
            sol += i
            if i != " ":
                start += 1
            if start >= longi:
                start = 0
        sol += Color.RESET
        return sol

    def __optend_hub(self, hub: Hub, connect: Connection, pos: int) -> Hub:
        """Return the hub corresponding to `pos` in `connect`.

        Parameters
        - hub: candidate hub to compare with connection endpoints
        - connect: connection object containing endpoint names
        - pos: 0 to select first endpoint, 1 to select second endpoint

        Returns
        - Hub: the matching hub or `self.hub` as fallback

        Raises
        - ValueError: if `pos` is not 0 or 1.
        """
        if pos not in (0, 1):
            raise ValueError("Fail, opten Hub in conection")
        if pos == 0:
            if hub.name == connect.name_first_hub:
                return hub
            return self.hub
        else:
            if hub.name == connect.name_second_hub:
                return hub
            return self.hub

    def __printer_connection(self, net: NetworkFly) -> str:
        """Return a string describing the connection the drone will use.

        Parameters
        - net: the current `NetworkFly` instance used to look up the
          connection object.

        Returns
        - str: formatted connection description for logging.

        Raises
        - ValueError: when the connection cannot be found in `net`.
        """
        hub = self.get_hub_route()
        key = frozenset((self.hub.name, hub.name))
        connect = net.found_connects(key)
        if connect is None:
            raise ValueError("Not found conection")
        first_hub = self.__optend_hub(hub, connect, 0)
        secon_hub = self.__optend_hub(hub, connect, 1)
        name = "'"
        if first_hub.color != Color.RAINBOW:
            name += self.__print_hub(first_hub.name, first_hub) + "-"
        else:
            name += self.__print_hub_rainbow(first_hub.name) + "-"
        if secon_hub.color != Color.RAINBOW:
            name += self.__print_hub(secon_hub.name, secon_hub) + "'"
        else:
            name += self.__print_hub_rainbow(secon_hub.name) + "'"
        text = f"D{self.id}-{name}"
        return text

    def get_hub_route(self, pos: int = 0) -> Hub:
        """Return the hub at the drone's route position + `pos`.

        Parameters
        - pos: offset from the drone's current `route_pos` (default 0)

        Returns
        - Hub: the hub object at the requested route index

        Raises
        - Found_hub_error: when the drone has no assigned route
        """
        if self.route is None:
            raise Found_hub_error(f"The Drone {self.id} hasn't rute")
        index = min(self.route_pos + pos, len(self.route) - 1)
        return self.route[index]

    def asign_rute(self, rute: list[Hub]) -> None:
        """Assign a route to the drone.

        Parameters
        - rute: full route including the current hub; the drone stores
          the tail of the route (excluding the current hub).
        """
        self.route = rute[1:]

    def verif_pos(self, position: Hub) -> bool:
        """Check whether the drone is currently at `position`.

        Parameters
        - position: the `Hub` to compare with the drone's current hub

        Returns
        - bool: True if the drone's `hub` equals `position`, else False.
        """
        return self.hub == position
