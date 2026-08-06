from typing import Optional
from generatorData import Hub, NetworkFly
from generatorData.enums import RAINBOW, Color
from random import randint
from dataclasses import dataclass
from excepcions import Found_hub_error


@dataclass
class Drones:

    id: int
    hub: Hub
    end_hub: Hub
    move: bool = False
    torns_sleep: int = 0
    in_air: bool = False
    route: Optional[list[Hub]] = None
    route_pos: int = 0

    def moves(self) -> str:
        if not self.move:
            self.move = True
        self.hub = self.get_hub_route()
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.in_air = False
        self.route_pos += 1
        return self.__printer()

    def wait(
            self,
            net: NetworkFly | None = None
            ) -> str | None:
        self.torns_sleep += 1
        if not self.in_air and self.move:
            return self.__printer()
        if net is not None:
            return self.__printer_connection(net)
        return None

    def __printer(self) -> str:
        text = f"D{self.id}-{self.hub.name}"
        sol = ""
        if self.hub.color != Color.RAINBOW:
            if isinstance(self.hub.color, str):
                sol += self.hub.color
            sol += text
            sol += Color.RESET
            return sol
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

    def __printer_connection(self, net: NetworkFly) -> str:
        hub = self.get_hub_route()
        key = frozenset((self.hub.name, hub.name))
        connect = net.found_connects(key)
        if connect is None:
            raise ValueError("Not found conection")
        name = f"'{connect.name_first_hub}-{connect.name_second_hub}'"
        text = f"D{self.id}-{name}"
        sol = ""
        if self.hub.color != Color.RAINBOW:
            if isinstance(self.hub.color, str):
                sol += self.hub.color
            sol += text
            sol += Color.RESET
            return sol
        longi = len(RAINBOW)
        start = randint(0, longi)
        for i in text:
            sol += RAINBOW[start % longi]
            sol += i
            if i != " ":
                start += 1
        sol += Color.RESET
        return sol

    def get_hub_route(self, pos: int = 0) -> Hub:
        if self.route is None:
            raise Found_hub_error(f"The Drone {self.id} hasn't rute")
        index = min(self.route_pos + pos, len(self.route) - 1)
        return self.route[index]

    def asign_rute(self, rute: list[Hub]) -> None:
        self.route = rute[1:]

    def verif_pos(self, position: Hub) -> bool:
        return self.hub == position
