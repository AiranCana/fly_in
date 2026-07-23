from generatorData import (Hub, NetworkFly, Connection,
                           Color, RAINBOW, Zones)
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
    in_air: bool = False
    stoped: bool = False

    def move_to(self, new_hub: Hub) -> str:
        if not self.move:
            self.move = True
        self.hub = new_hub
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.in_air = False
        return self.printer()

    def wait(self) -> str | None:
        self.torns_sleep += 1
        if self.move:
            return self.printer()

    def printer(self) -> None:
        text = f"D{self.id}-{self.hub.name}"
        sol = ""
        if self.hub.color != Color.RAINBOW:
            sol = self.hub.color
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


class Simulation:

    def __init__(self, net: NetworkFly):
        self._net: NetworkFly = net
        self.zone_count: dict[str, int] = {
            hub.name: 0 for hub in self.__all_hubs()
        }
        self.connect_count: dict[frozenset[str], int] = {
            self.conection_key(c): 0 for c in self._net.connections
        }
        self.zone_count[net.start_hub.name] = net.nb_drones

    def __all_hubs(self) -> list[Hub]:
        return [self._net.start_hub, self._net.end_hub,
                *self._net.hubs]

    def conection_key(self, connect: Connection) -> frozenset[str]:
        return frozenset((connect.name_first_hub,
                         connect.name_second_hub))

    def is_unlimited(self, hub: Hub) -> bool:
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


class Operate:

    def __init__(self, drones: list[Drones], simul: Simulation):
        self.drone = drones
        self.simul = simul
        self.turn = 1

    def __get_connection(self, hub: Hub, drone: int) -> Connection:
        first = self.simul._net.found_connects(hub)
        second = self.simul._net.found_connects(self.drone[drone].hub)
        conection = list(set(first) & set(second))
        if len(conection) == 0:
            raise Found_hub_error(f"The connection beetwen {hub.name} "
                                  f"and {self.drone[drone].hub.name} dosen't"
                                  " exist")
        return conection[0]

    def can_enter_hub(self, hub: Hub, drone: int) -> bool:
        if self.simul.is_unlimited(hub):
            return True
        number = self.simul.zone_count.get(hub.name, None)
        if not isinstance(number, int):
            raise Found_hub_error(f"Cannot enter '{hub.name}': no "
                                  "drone there")
        if isinstance(number, int) and (
           number + 1 > hub.max_drones or hub.zone == Zones.BLOCKED):
            return False
        conection = self.__get_connection(hub, drone)
        key = self.simul.conection_key(conection)
        data = self.simul.connect_count[key] + 1
        if data > conection.max_link_capacity:
            return False
        return True

    def prepare_move(
            self, hub: Hub, drone: int
         ) -> None | dict[Drones, tuple[Hub, Connection]]:
        conection = self.__get_connection(hub, drone)
        key = self.simul.conection_key(conection)
        if self.can_enter_hub(hub, drone):
            if not self.drone[drone].in_air:
                self.simul.connect_count[key] += 1
                self.simul.zone_count[self.drone[drone].hub.name] -= 1
                self.drone[drone].in_air = True
                return {self.drone: (hub, conection, True)}
        return {self.drone: (hub, conection, False)}

    def can_move_now(self, hub: Hub, drone: int) -> bool:
        if hub.zone == Zones.RESTRICTED and self.drone[drone].torns_sleep < 2:
            return False
        return True

    def movement(self, move: dict[Drones, tuple[Hub, Connection]]) -> None:
        print(f"Turn {self.turn}: ", end="")
        for dro, item in move.items():
            hub, connect, move = item
            key = self.simul.conection_key(connect)
            content = []
            if move:
                if self.can_move_now(hub, self.drone[dro]):
                    self.simul.connect_count[key] -= 1
                    content.append(self.drone[dro].move_to(hub))
                    self.simul.zone_count[hub.name] += 1
                    continue
            content.append(self.drone[dro].wait())
        print(*content, sep=", ")
        self.turn += 1
