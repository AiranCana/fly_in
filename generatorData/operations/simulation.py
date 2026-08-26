"""Simulation state container used by the operator and drones.

This module defines `Simulation`, which holds hub occupancy and link
usage counters and provides utility helpers consumed by `Operate`.
"""

from generatorData import NetworkFly, Connection, Hub
from excepcions import Found_hub_error
from generatorData.generateRutes import Generator


class Simulation:
    """Holds runtime counters and provides helpers for simulation logic.

    The simulation tracks how many drones occupy each hub and how many
    drones are currently traversing each connection.
    """

    def __init__(self, net: NetworkFly):
        """Initialise counters for the provided network.

        The start hub is initially populated with all configured drones.
        """
        self._net: NetworkFly = net
        self.zone_count: dict[str, int] = {
            hub.name: 0 for hub in self.__all_hubs()
        }
        self.connect_count: dict[frozenset[str], int] = {
            self.conection_key(c): 0 for c in self._net.connections
        }
        self.zone_count[net.start_hub.name] = net.nb_drones

    def __all_hubs(self) -> list[Hub]:
        """Return a list containing start, end and all intermediate hubs.

        The list is ordered as [start_hub, end_hub, *hubs].
        """
        return [self._net.start_hub, self._net.end_hub,
                *self._net.hubs]

    def conection_key(self, connect: Connection) -> frozenset[str]:
        """Return a frozenset key identifying `connect` for counters.

        The returned frozenset is used as a stable dictionary key for
        `connect_count` lookups independent of hub ordering.
        """
        return frozenset((connect.name_first_hub,
                         connect.name_second_hub))

    def is_unlimited(self, hub: Hub) -> bool:
        """Return True if `hub` is a start/end hub (unlimited capacity).

        Start and end hubs are treated as having unlimited capacity for
        the purposes of occupancy accounting.
        """
        return hub.name in (self._net.start_hub.name,
                            self._net.end_hub.name)

    def free_old_hub(self, name: str) -> None:
        """Decrement occupancy counter for `name`, or raise if not present.

        Parameters
        - name: hub name to decrement

        Raises
        - Found_hub_error: when `name` is not present in the simulation
          zone counters.
        """
        if name in self.zone_count:
            self.zone_count[name] -= 1
            return
        raise Found_hub_error(f"Cannot free '{name}': no drone there")

    def asign_new_hub(self, name: str) -> None:
        """Increment occupancy counter for `name`, or raise if not present.

        Parameters
        - name: hub name to increment

        Raises
        - Found_hub_error: when `name` is not present in the simulation
          zone counters.
        """
        if name in self.zone_count:
            self.zone_count[name] += 1
            return
        raise Found_hub_error(f"Cannot asign '{name}': no drone there")

    def generate_rute(self) -> list[list[Hub]]:
        """Create and return route candidates using the generator.

        Returns
        - list[list[Hub]]: a list of candidate routes, each being a list of
          `Hub` objects from start to end.
        """
        gen: Generator = Generator(self._net)
        return gen.generate_rute()
