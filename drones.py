from generatorData import (Hub, NetworkFly, Connection,
                           Color, RAINBOW)
from random import randint
from dataclasses import dataclass
from excepcions import Found_hub_error


@dataclass
class Drones:

    id: int
    hub: Hub
    end_hub: Hub
    move = False
    torns_sleep: int = 0

    def move_to(self, new_hub: Hub | None,
                simulation: "Simulation") -> None:
        if not new_hub:
            self.wait()
            return
        if not self.move:
            self.move = True
        simulation.free_old_hub(self.hub.name)
        self.hub = new_hub
        simulation.asign_new_hub(self.hub.name)
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.printer()

    def wait(self) -> None:
        self.torns_sleep += 1
        if self.move:
            self.printer()

    def printer(self) -> None:
        text = f"D{self.id}-{self.hub.name}"
        if self.hub.color != Color.RAINBOW:
            print(self.hub.color, end="")
            print(text, end="")
            print(Color.RESET, end="")
            return
        longi = len(RAINBOW)
        start = randint(0, longi)
        for i in text:
            print(RAINBOW[start % longi], end="")
            print(i, end="")
            if i != " ":
                start += 1
        print(Color.RESET, end="")


class Simulation:

    def __init__(self, net: NetworkFly):
        self._net: NetworkFly = net
        self.zone_count: dict[str, int] = {
            hub.name: 0 for hub in self.__all_hubs()
        }
        self.connect_count: dict[frozenset[str], int] = {
            self.__conection_key(c): 0 for c in self._net.connections
        }
        self.zone_count[net.start_hub.name] = net.nb_drones

    def __all_hubs(self) -> list[Hub]:
        return [self._net.start_hub, self._net.end_hub,
                *self._net.hubs]

    def __conection_key(self, connect: Connection) -> frozenset[str]:
        return frozenset((connect.name_first_hub,
                         connect.name_second_hub))

    def __is_unlimited(self, hub: Hub) -> bool:
        return hub.name in (self._net.start_hub.name,
                            self._net.end_hub.name)
    
    def free_old_hub(self, name: str) -> None:
        if name in self.zone_count:
            self.zone_count[name] -= 1
            return
        raise Found_hub_error(f"Cannot free '{name}': no drone there")

    def asign_new_hub(self, name: str) -> None:
        if name in self.zone_count:
            self.zone_count[name] += 1
            return
        raise Found_hub_error(f"Cannot asign '{name}': no drone there")

    def can_enter_hub(self, hub: Hub) -> bool:
        if self.__is_unlimited(hub):
            return True
        number = self.zone_count.get(hub.name, None)
        if number == None:
            raise Found_hub_error(f"Cannot enter '{hub.name}': no "
                                  "drone there")
        if number >= hub.max_drones:
            return False
        