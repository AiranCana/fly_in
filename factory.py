from generatorData import Hub, NetworkFly
from drones import Drones, Simulation, Operate


def factory_drones(number: int, start: Hub, end: Hub) -> list[Drones]:
    x = [Drones(i + 1, start, end) for i in range(number)]
    return x


def factory_simulation(net: NetworkFly) -> Simulation:
    return Simulation(net)


def factory_operate(lis: list[Drones], simu: Simulation) -> Operate:
    return Operate(lis, simu)
