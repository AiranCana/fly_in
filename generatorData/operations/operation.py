"""Operator logic that advances drones through the simulation.

This module provides the `Operate` class that manages drone assignments,
moves and turn progression for a given `Simulation` instance.
"""

from generatorData import Hub, Connection
from ..enums import Color, Zones
from excepcions import Found_hub_error, Movements_errors
from .drones import Drones
from .simulation import Simulation
from time import sleep


CYAN = "\033[38;2;0;180;180m"
RESET = Color.RESET


class Operate:
    """Controller coordinating drone movement along assigned routes.

    The `Operate` instance owns a list of `Drones` and a `Simulation`
    object and exposes methods to compute which drones should move on
    each turn and to apply those movements.
    """

    def __init__(
               self,
               drones: list[Drones],
               simul: Simulation
            ):
        """Initialise an operator with drones and a simulation.

        Assigns routes to drones proportionally to route capacities.
        """
        self.drones = drones
        self.simul = simul
        self.turn = 1
        self.route = self.simul.generate_rute()

        self.__prepare_asign_route(self.route)

    def __get_connection(self, pos_dron: int) -> Connection:
        """Return the `Connection` object between a drone and its next hub.

        Parameters
        - pos_dron: index of the drone to inspect

        Returns
        - Connection: the shared connection object between current and
          next hub for the drone
        """
        drone = self.drones[pos_dron]
        hub = drone.get_hub_route()
        first = self.simul._net.found_connects(hub)
        second = self.simul._net.found_connects(drone.hub)
        conection = list(set(first) & set(second))
        if len(conection) == 0:
            raise Found_hub_error(f"The connection beetwen {hub.name} "
                                  f"and {drone.hub.name} dosen't"
                                  " exist")
        return conection[0]

    def __can_fly(self, pos_dron: int) -> bool:
        """Return True if the drone at `pos_dron` can traverse its connection.

        Checks link capacity and destination hub occupancy constraints.
        """
        drone = self.drones[pos_dron]
        conection = self.__get_connection(pos_dron)
        key = self.simul.conection_key(conection)
        data = self.simul.connect_count[key]
        if not drone.in_air:
            data += 1
        if data > conection.max_link_capacity:
            return False
        hub = drone.get_hub_route()
        data_hub = self.simul.zone_count[hub.name]
        if ((data + data_hub) > hub.max_drones and
           hub != self.simul._net.end_hub):
            return False
        return True

    def __can_enter_hub(self, pos_dron: int) -> bool:
        """Decide if the drone can enter its next hub given current state.

        Considers unlimited hubs, occupancy counters and blocked/restricted
        zones.
        """
        drone = self.drones[pos_dron]
        hub = drone.get_hub_route()
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
        """Prepare a potential move for drone at `pos_dron`.

        Returns a mapping `{pos: (connection, can_move_flag)}` when the
        drone is eligible to attempt movement, or `None`-like structure
        indicating the move outcome.
        """
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
        """Return True if the drone may move this turn considering waits.

        Enforces per-hub turn-wait rules (e.g., restricted zones).
        """
        drone = self.drones[pos_dron]
        hub = drone.get_hub_route()
        if hub.zone == Zones.RESTRICTED and drone.torns_sleep < 1:
            return False
        return True

    def __movement(
            self,
            move: dict[int, tuple[Connection, bool]],
            printer: bool
            ) -> dict[int, list[Drones]]:
        """Execute the prepared `move` mapping, performing state updates.

        Parameters
        - move: mapping from drone index to (Connection, can_move_flag)
        - printer: whether to print turn output

        Returns
        - dict[int, list[Drones]]: snapshot of drone states for the turn
        """
        if printer:
            print(f"{CYAN}Turn {self.turn}: {RESET}", end="")
        content = []
        for dro, item in move.items():
            connect, camn_move = item
            drone = self.drones[dro]
            hub = drone.get_hub_route()
            key = self.simul.conection_key(connect)
            if camn_move:
                if self.__can_move_now(dro):
                    self.simul.connect_count[key] -= 1
                    content.append(self.drones[dro].moves())
                    self.simul.zone_count[hub.name] += 1
                    continue
                result = self.drones[dro].wait(self.simul._net)
                if isinstance(result, str):
                    content.append(result)
                continue
            result = self.drones[dro].wait()
            if isinstance(result, str):
                content.append(result)
        if printer:
            print(*content, sep=", ")
        self.turn += 1
        new_drones = [Drones(**d.__dict__) for d in self.drones]
        return {self.turn - 1: new_drones}

    def __calculate_weight_rute(self, route: list[Hub]) -> int:
        """Compute a weight for a route based on hub/link capacities.

        The returned integer is used to proportionally assign drones.
        """
        limits: list[int] = []
        for hub in route[1: -1]:
            limits.append(hub.max_drones)
        for hub1, hub2 in zip(route, route[1:]):
            key = frozenset((hub1.name, hub2.name))
            connect = self.simul._net.found_connects(key)
            if connect is not None:
                limits.append(connect.max_link_capacity)
        return min(limits) if limits else 1

    def __prepare_asign_route(self, routes: list[list[Hub]]) -> None:
        """Compute assignment weights and delegate to `__asign_route`.

        This computes proportional allocation based on route capacities.
        """
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
        self.__asign_route(routes, weights, n_drones, base_drones_in_routes)

    def __asign_route(
            self,
            routes: list[list[Hub]],
            weights: list[int],
            n_drones: int,
            base_drones_in_routes: list[int]
            ) -> None:
        """Assign each drone to one of the candidate `routes`.

        Uses `weights` and base quotas to distribute `n_drones`.
        """
        assignment: list[int] = [-1] * n_drones
        counter = list(base_drones_in_routes)
        order_route = sorted(range(len(routes)),
                             key=lambda i: -weights[i])
        pos = 0
        while any(p > 0 for p in counter):
            for route_id in order_route:
                if counter[route_id] > 0 and pos < n_drones:
                    assignment[pos] = route_id
                    pos += 1
                    counter[route_id] -= 1
        for dron, route in zip(self.drones, assignment):
            if 0 < len(routes):
                dron.asign_rute(routes[route])
            else:
                raise Movements_errors("No exit has been found")

    def turns(self, targets: list[int], printer: bool = True
              ) -> dict[int, list[Drones]] | None:
        """Execute a single turn for the provided target drone indices.

        Parameters
        - targets: list of drone indices chosen to attempt movement this
          turn
        - printer: if True print turn/log messages to stdout

        Returns
        - dict[int, list[Drones]] | None: snapshot mapping the turn
          number to a shallow-copied list of drone states when movement
          occurred; `None` if no movement happened.

        Raises
        - Found_hub_error, Movements_errors: propagated from drone and
          simulation operations when invalid moves are attempted.
        """
        moves: dict[int, tuple[Connection, bool]] = {}
        for drone in targets:
            prep = self.__prepare_move(drone)
            if prep:
                moves.update(prep)
        if len(moves) != 0:
            return self.__movement(moves, printer)
        return None

    def is_finished(self) -> bool:
        """Return True when all drones have reached the simulation end hub.

        Returns
        - bool: True if every drone's `hub` equals the network `end_hub`.
        """
        return all(d.hub == self.simul._net.end_hub for d in self.drones)

    def run(self, printer: bool = True) -> int:
        """Run the simulation until all drones reach the end hub.

        Parameters
        - printer: when True, intermediate turn output is printed

        Returns
        - int: number of turns elapsed when the simulation finishes
        """
        turn: int = 1
        while not self.is_finished():
            lis: list[int] = self.order_target()
            _ = self.turns(lis, printer)
            if not self.is_finished():
                turn += 1
            if printer:
                sleep(0.5)
        return turn

    def order_target(self) -> list[int]:
        """Return a prioritized list of drone indices for the next turn.

        Drones that have not reached `end_hub` are returned sorted by the
        number of remaining steps (ascending) and by drone id as tiebreaker.
        """
        end = self.simul._net.end_hub
        archives = [i for i, d in enumerate(self.drones)
                    if not d.verif_pos(end)]
        archives.sort(key=lambda i: (self.__remaining_steps(i),
                                     self.drones[i].id))
        return archives

    def __remaining_steps(self, pos: int) -> int:
        """Compute remaining route steps for drone at index `pos`.

        Returns
        - int: count of remaining hubs in the drone's assigned `route`.
        """
        dron = self.drones[pos]
        if dron.route is not None:
            return len(dron.route) - dron.route_pos
        return 0
