from generatorData import Hub, Connection, Zones
from excepcions import Found_hub_error
from operations import Simulation, Drones


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

    def __can_fly(self, pos_dron: int) -> bool:
        dron = self.drones[pos_dron]
        conection = self.__get_connection(pos_dron)
        key = self.simul.conection_key(conection)
        data = self.simul.connect_count[key]
        if not dron.in_air:
            data += 1
        if data > conection.max_link_capacity:
            return False
        return True

    def __can_enter_hub(self, pos_dron: int) -> bool:
        dron = self.drones[pos_dron]
        hub = dron.get_rute()
        if self.simul.is_unlimited(hub):
            return self.__can_fly(pos_dron)
        number = self.simul.zone_count.get(hub.name, None)
        if not isinstance(number, int):
            raise Found_hub_error(f"Cannot enter '{hub.name}': no "
                                  "pos_dron there")
        if isinstance(number, int) and (
           number + 1 > hub.max_drones or hub.zone == Zones.BLOCKED):
            return False
        return self.__can_fly(pos_dron)

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
            result = self.drones[dro].wait(self.simul._net.found_connects)
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
        n_drones = len(self.drones)
        exact_drones_in_routes = [n_drones * w / total_weight for w in weights]
        base_drones_in_routes = [int(ex) for ex in exact_drones_in_routes]
        remainders = [ex - bas for ex, bas in zip(exact_drones_in_routes,
                                                  base_drones_in_routes)]
        leftover = n_drones - sum(base_drones_in_routes)
        order = sorted(range(len(routes)),
                       key=lambda i: remainders[i],
                       reverse=True)
        for i in order[:leftover]:
            base_drones_in_routes[i] += 1
        assignment: list[int] = []
        for route_idx, count in enumerate(base_drones_in_routes):
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
