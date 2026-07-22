from generatorData import Hub, NetworkFly
from drones import Drones, Simulation

def factory_drones(number: int, start: Hub, end: Hub) -> list[Drones]:
    return [Drones(i + 1, start, end) for i in range(number)]

def factory_simulation(net: NetworkFly) -> Simulation:
    return Simulation(net)