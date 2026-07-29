from typing import Optional, Callable
from generatorData import (Hub, Connection,
                           Color, RAINBOW)
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
        self.hub = self.get_rute()
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.in_air = False
        self.route_pos += 1
        return self.__printer()

    def wait(
            self,
            funtion: Optional[Callable[..., Connection]] = None
            ) -> str | None:
        self.torns_sleep += 1
        if not self.in_air:
            return self.__printer()
        if funtion is not None:
            return self.__printer_connection(funtion)
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

    def __printer_connection(self, funtion: Callable[..., Connection]) -> str:
        connect = funtion()
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

    def get_rute(self) -> Hub:
        if self.route is None:
            raise Found_hub_error(f"The Drone {self.id} hasn't rute")
        return self.route[self.route_pos]

    def asign_rute(self, rute: list[Hub]) -> None:
        self.route = rute
