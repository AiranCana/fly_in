from typing import Optional
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
    move: bool = False
    torns_sleep: int = 0
    in_air: bool = False
    rute: Optional[list[Hub]] = None
    rute_pos: int = 0

    def moves(self) -> str:
        if not self.move:
            self.move = True
        self.hub = self.get_rute()
        if self.hub == self.end_hub:
            self.move = False
        self.torns_sleep = 0
        self.in_air = False
        self.rute_pos += 1
        return self.__printer()

    def wait(self) -> str | None:
        self.torns_sleep += 1
        if self.move:
            return self.__printer()
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
        sol += Color.RESET
        return sol

    def get_rute(self) -> Hub:
        hub = self.rute[self.rute_pos]
        if not hub:
            raise Found_hub_error(f"The Drone {self.id} hasn't rute")
        return hub

    def asign_rute(self, rute: list[Hub]) -> None:
        self.rute = rute


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
        raise Found_hub_error(f"Cannot free '{name}': no dron there")

    def asign_new_hub(self, name: str) -> None:
        if name in self.zone_count:
            self.zone_count[name] += 1
            return
        raise Found_hub_error(f"Cannot asign '{name}': no dron there")

    def generate_rute(self) -> list[list[Hub]]:
        ...


class Operate:

    def __init__(self, drones: list[Drones], simul: Simulation):
        self.drones = drones
        self.simul = simul
        self.turn = 1
        route = self.simul.generate_rute()
        self.__asign_route(route)

    def __get_connection(self, pos_dron: int) -> Connection:
        dron = self.drones[pos_dron]
        hub = dron.get_rute()
        first = self.simul._net.found_connects(hub)
        second = self.simul._net.found_connects(dron.hub)
        conection = list(set(first) & set(second))
        if len(conection) == 0:
            raise Found_hub_error(f"The connection beetwen {hub.name} "
                                  f"and {dron.hub.name} dosen't"
                                  " exist")
        return conection[0]

    def __can_enter_hub(self, pos_dron: int) -> bool:
        dron = self.drones[pos_dron]
        hub = dron.get_rute()
        if self.simul.is_unlimited(hub):
            return True
        number = self.simul.zone_count.get(hub.name, None)
        if not isinstance(number, int):
            raise Found_hub_error(f"Cannot enter '{hub.name}': no "
                                  "pos_dron there")
        if isinstance(number, int) and (
           number + 1 > hub.max_drones or hub.zone == Zones.BLOCKED):
            return False
        conection = self.__get_connection(pos_dron)
        key = self.simul.conection_key(conection)
        data = self.simul.connect_count[key]
        if not dron.in_air:
            data += 1
        if data > conection.max_link_capacity:
            return False
        return True

    def __prepare_move(
            self, pos_dron: int
         ) -> None | dict[int, tuple[Connection, bool]]:
        conection = self.__get_connection(pos_dron)
        key = self.simul.conection_key(conection)
        if self.__can_enter_hub(pos_dron):
            if not self.drones[pos_dron].in_air:
                self.simul.connect_count[key] += 1
                self.simul.zone_count[self.drones[pos_dron].hub.name] -= 1
                self.drones[pos_dron].in_air = True
                self.drones[pos_dron].torns_sleep = 0
                return {pos_dron: (conection, True)}
            return {pos_dron: (conection, True)}
        return {pos_dron: (conection, False)}

    def __can_move_now(self, pos_dron: int) -> bool:
        dron = self.drones[pos_dron]
        hub = dron.get_rute()
        if hub.zone == Zones.RESTRICTED and dron.torns_sleep < 1:
            return False
        return True

    def __movement(
            self,
            move: dict[int, tuple[Connection, bool]]
            ) -> None:
        print(f"Turn {self.turn}: ", end="")
        content = []
        for dro, item in move.items():
            connect, camn_move = item
            dron = self.drones[dro]
            hub = dron.get_rute()
            key = self.simul.conection_key(connect)
            if camn_move:
                if self.__can_move_now(dro):
                    self.simul.connect_count[key] -= 1
                    content.append(self.drones[dro].moves())
                    self.simul.zone_count[hub.name] += 1
                    continue
            result = self.drones[dro].wait()
            if isinstance(result, str):
                content.append(result)
        print(*content, sep=", ")
        self.turn += 1

    def __calculate_weight_rute(self, route: list[Hub]) -> int:
        limits: list[int] = []
        for hub in route[1: -1]:
            limits.append(hub.max_drones)
        for hub1, hub2 in zip(route, route[1:]):
            key = frozenset((hub1.name, hub2.name))
            connect = self.simul._net.found_connects(key)
            if connect is not None:
                limits.append(connect.max_link_capacity)
        return min(limits) if limits else 1

    def __asign_route(self, routes: list[list[Hub]]) -> None:
        weights = [self.__calculate_weight_rute(r) for r in routes]
        total_weight = sum(weights)
        n = len(self.drones)
        exact_shares = [n * w / total_weight for w in weights]
        base_shares = [int(s) for s in exact_shares]
        remainders = [s - b for s, b in zip(exact_shares, base_shares)]
        leftover = n - sum(base_shares)
        order = sorted(range(len(routes)), key=lambda i : remainders[i],
                             reverse=True)
        for i in order[:leftover]:
            base_shares[i] += 1
        assignment: list[int] = []
        for route_idx, count in enumerate(base_shares):
            assignment.extend([route_idx] * count)
        for dron, route_idx in zip(self.drones, assignment):
            dron.asign_rute(routes[route_idx])

    def __torns(self, targets: list[int], torn: int) -> None:
        moves: dict[int, tuple[Connection, bool]] = {}
        for dron in targets:
            prep = self.__prepare_move(dron)
            if prep:
                moves.update(prep)
        if len(moves) != 0:
            print(f"torn {torn}: ", end="")
            self.__movement(moves)

    def __is_finished(self) -> bool:
        return all(d.hub == self.simul._net.end_hub for d in self.drones)

    def run(self) -> None:
        torn: int = 1
        while self.__is_finished():
            lis: list[int] = []
            pass
            self.__torns(lis, torn)
            torn += 1
