from .genDataZones import NetworkFly, Hub
from .enums import Zones
import heapq


class Generator:

    FACTOR_COST = 1.0005

    def __init__(self, net: NetworkFly):
        self._net = net

    def __zone_cost(self, hub: Hub) -> int:
        if hub.zone == Zones.RESTRICTED:
            return 2
        return 1

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

    def __dijkstra(
            self,
            start: Hub,
            end: Hub,
            connection: frozenset[frozenset[str]] = frozenset()
            ) -> list[Hub] | None:
        distances: dict[str, float] = {start.name: 0.0}
        previus: dict[str, Hub] = {}
        distances, previus = self.__optend_first_path(
            start, end, connection, distances, previus)
        if end.name not in distances:
            return None
        path: list[Hub] = [end]
        current = end.name
        while current != start.name:
            prev_hub = previus[current]
            path.append(prev_hub)
            current = prev_hub.name
        path.reverse()
        return path

    def __optend_first_path(
            self, start: Hub, end: Hub,
            connection: frozenset[frozenset[str]],
            distances: dict[str, float], previus: dict[str, Hub]) -> tuple[
                dict[str, float], dict[str, Hub]]:
        visited: set[str] = set()
        heap: list[tuple[float, str, Hub]] = [(0.0, start.name, start)]
        while heap:
            dist, name, hub = heapq.heappop(heap)
            if name in visited:
                continue
            visited.add(name)
            if name == end.name:
                break
            distances, previus, heap = self.explore_neighbor(
                connection, distances, previus, heap, dist, name, hub)
        return (distances, previus)

    def explore_neighbor(
            self, connection: frozenset[frozenset[str]],
            distances: dict[str, float], previus: dict[str, Hub],
            heap: list[tuple[float, str, Hub]],
            dist: float, name: str, hub: Hub) -> tuple[
                dict[str, float], dict[str, Hub], list[tuple[float, str, Hub]]
            ]:
        def tie_break(hub: Hub) -> float:
            return -0.001 if hub.zone == Zones.PRIORITY else 0.0
        resultado = self._net.found_connects(hub)
        for connect in resultado:
            neighbor_name = (
                    connect.name_second_hub
                    if connect.name_first_hub == name
                    else connect.name_first_hub
                )
            key = frozenset((connect.name_first_hub,
                             connect.name_second_hub))
            if key in connection:
                continue
            neighbor = self._net.hub_by_name.get(neighbor_name)
            if neighbor is None or neighbor.zone == Zones.BLOCKED:
                continue
            new_dist = (
                dist + self.__zone_cost(neighbor) + tie_break(neighbor)
                )
            if new_dist < distances.get(neighbor_name, float("inf")):
                distances[neighbor_name] = new_dist
                previus[neighbor_name] = hub
                heapq.heappush(heap, (new_dist, neighbor_name, neighbor))
        return (distances, previus, heap)

    def generate_rute(self) -> list[list[Hub]]:
        nb_drones = self._net.nb_drones
        start, end = self._net.start_hub, self._net.end_hub
        first = self.__dijkstra(start, end)
        if first is None:
            return []
        paths: list[list[Hub]] = [first]
        duplicate: set[tuple[str, ...]] = {tuple(h.name for h in first)}
        best_cost = self.__path_cost(first)
        accumulate_enter = self.__bottleneck(first)
        while accumulate_enter < nb_drones:
            best_candidate: list[Hub] | None = None
            best_candidate_cost = float("inf")
            for path in paths:
                for a, b in zip(path, path[1:]):
                    connect = frozenset({frozenset((a.name, b.name))})
                    candidate = self.__dijkstra(start, end, connect)
                    if candidate is None:
                        continue
                    key = tuple(h.name for h in candidate)
                    if key in duplicate:
                        continue
                    cost = self.__path_cost(candidate)
                    if cost < best_candidate_cost:
                        best_candidate_cost = cost
                        best_candidate = candidate
            if best_candidate is None:
                break
            if best_candidate_cost > best_cost * self.FACTOR_COST:
                break
            paths.append(best_candidate)
            duplicate.add(tuple(h.name for h in best_candidate))
            accumulate_enter += self.__bottleneck(best_candidate)
        paths.sort(key=lambda i: len(i))
        return paths
