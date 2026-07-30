from generatorData import NetworkFly, Hub, Zones


class Generator:

    FACTOR_COST = 1.5

    def __init__(self, net: NetworkFly):
        self._net = net

    def __zone_cost(self, hub: Hub) -> int:
        if hub.zone == Zones.RESTRICTED:
            return 2
        return 1

    def tie_break(hub: Hub) -> float:
        return -0.001 if hub.zone == Zones.PRIORITY else 0.0

    def __path_cost(self, path: list[Hub]) -> int:
        return sum(self.__zone_cost(h) for h in path)

    def __bottleneck(self, path: list[Hub]) -> int:
        limit: list[int] = [h.max_drones for h in path[1: -1]]
        for a, b in zip(path, path[1:]):
            key = frozenset((a.name, b.name))
            connect = self._net.found_connects(key)
            if connect is not None:
                limit.append(connect.max_link_capacity)
        return min(limit) if limit else 1
