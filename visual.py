"""Pygame-based visualization for the drone network simulation.

This module provides functions to display hubs, connections and animate
the movement of drones over time using `pygame`.
"""

import pygame
from pygame import Surface
from pygame.time import Clock
from generatorData import NetworkFly, Drones, Hub, Operate, Zones
import colorsys
from time import time


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (127, 127, 127)
YELLOW = (255, 255, 0)
BACKGROUND = (25, 25, 25)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
font = None
pos: dict[int, list[Drones]] = {}


class Drones_pos:
    """Runtime helper holding a drone and its screen position.

    Encapsulates current and future screen coordinates, and previous
    hub/in-air state used to animate transitions.
    """

    def __init__(self, drone: Drones, pos: Hub):
        """Initialise a `Drones_pos` helper with a drone and hub position.

        Parameters
        - drone: the `Drones` instance to track
        - pos: the `Hub` providing initial screen coordinates
        """
        self.drone = drone
        self.x = pos.x*150 + 50
        self.y = pos.y*150 + 350
        self.__future_x = pos.x*150 + 50
        self.__future_y = pos.y*150 + 350
        self.pre_hub = pos
        self.pre_in_air = drone.in_air

    def get__future_pos(self) -> tuple[int, int]:
        """Return the computed future screen position (x, y).

        Returns
        - tuple[int, int]: future (x, y) coordinates used for animation
        """
        return (self.__future_x, self.__future_y)

    def set__future_pos(self, midel: bool = False) -> None:
        """Compute and set the future screen position for the drone.

        Parameters
        - midel: when True compute the midpoint between origin and
          destination (used for in-air animation), otherwise set the
          destination coordinates.
        """
        if not midel:
            hub = self.drone.hub
            x = hub.x*150 + 50 - self.x
            y = hub.y*150 + 350 - self.y
            self.__future_x = x + self.x
            self.__future_y = y + self.y
        else:
            origin = self.drone.hub
            destiny = self.drone.get_hub_route()
            origen_x = origin.x*150 + 50
            origen_y = origin.y*150 + 350
            destino_x = destiny.x*150 + 50
            destino_y = destiny.y*150 + 350
            self.__future_x = origen_x + (destino_x - origen_x) // 2
            self.__future_y = origen_y + (destino_y - origen_y) // 2


def visual(net: NetworkFly, name_windos: str) -> None:
    """Start a pygame window and run the visualization for `net`.

    `name_windos` is used as the window title.
    """
    global font
    ope1: Operate = net.create_Opertor()
    ope: Operate = net.create_Opertor()
    new_drones = [Drones(**d.__dict__) for d in ope1.drones]
    pos.update({0: new_drones})
    while not ope1.is_finished():
        lis: list[int] = ope1.order_target()
        pos.update(ope1.turns(lis))
    pygame.init()
    font = pygame.font.SysFont("Arial", 14, bold=True)
    width, height = order_list(ope)
    drones = [Drones_pos(dro, dro.hub) for dro in ope.drones]
    WIDTH = (max(width) - min(width)) * 150 + 150
    HEIGHT = (max(height) - min(height)) * 150 + 450
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(name_windos)
    clock = pygame.time.Clock()
    running = True

    print_animation(ope, drones, window, clock, running)
    pygame.quit()


def order_list(ope: Operate) -> tuple[list[int], list[int]]:
    """Return lists of hub x and y coordinates used to size the window.

    The returned tuple contains two lists: the x coordinates and the y
    coordinates of all hubs (including start and end) used to compute
    the window size.
    """
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    width = [hub.x for hub in lis]
    height = [hub.y for hub in lis]
    return width, height


def print_animation(
        ope: Operate,
        drones: list[Drones_pos],
        window: Surface,
        clock: Clock,
        running: bool) -> None:
    """Main animation loop: handle events and step frames until finished.

    Processes pygame events, updates drone snapshots and renders frames
    until the simulation completes or the user quits.
    """
    times = time()
    posittion = 0
    drones = [Drones_pos(dro, dro.hub) for dro in pos[0]]
    while running:
        move = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in (pygame.K_RIGHT, pygame.K_d,
                                 pygame.K_LEFT, pygame.K_a):
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        if posittion + 1 < len(pos):
                            posittion += 1
                            move = True
                    else:
                        if posittion > 0:
                            posittion -= 1
                            move = True
        if move:
            new_snapshot = pos[posittion]
            for dp, new_dro in zip(drones, new_snapshot):
                dp.pre_hub = dp.drone.hub
                dp.pre_in_air = dp.drone.in_air
                dp.drone = new_dro
        draw_drones(drones, ope, window, times, move)
        move = False
        if (ope.is_finished()):
            pygame.time.delay(250)
            running = False
        clock.tick(60)


def draw_hubs(ope: Operate, window: Surface, times: float) -> None:
    """Draw all hubs, using explicit colors when provided.

    Hubs with a configured color will be drawn using that color; other
    hubs are rendered with an animated rainbow effect.
    """
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    for hub in lis:
        if hub.color is not None:
            new_ccolor = hub.color
            if len(new_ccolor) != 0:
                data = new_ccolor.strip("m").split(";")
                color = (int(data[-3]), int(data[-2]), int(data[-1]))
                draw_hub(window, hub, color)
            else:
                draw_hub_rainbow(window, hub, times)
        else:
            draw_hub_rainbow(window, hub, times)


def draw_hub_rainbow(window: Surface, hub: Hub, times: float) -> None:
    """Draw a hub with a rainbow animation.

    Used for hubs that do not have a static color configuration. The
    function also draws a labeled name under the hub marker.
    """
    if hub.zone == Zones.RESTRICTED:
        colore = YELLOW
    elif hub.zone == Zones.PRIORITY:
        colore = GREEN
    elif hub.zone == Zones.NORMAL:
        colore = WHITE
    else:
        colore = RED
    if hub.zone != Zones.NORMAL:
        pygame.draw.circle(window, colore,
                           (hub.x*150 + 50, hub.y*150 + 350), 27, 4)
        pygame.draw.circle(window, BACKGROUND,
                           (hub.x*150 + 50, hub.y*150 + 350), 23, 4)
    current_time = time() - times
    offset = (current_time * 0.15) % 1.0

    for r in range(20, 0, -1):
        hue = (r / 20 + offset) % 1.0
        r_col, g_col, b_col = colorsys.hsv_to_rgb(hue, 1, 1)
        color = (int(r_col * 255), int(g_col * 255), int(b_col * 255))
        pygame.draw.circle(window, color,
                           (hub.x*150 + 50, hub.y*150 + 350), r)
    text = font.render(f"{hub.name}", True, WHITE)
    center_text = text.get_rect(center=(hub.x*150 + 50, hub.y*150 + 385))
    window.blit(text, center_text)


def draw_hub(window: Surface, hub: Hub, color: tuple[int, int, int]) -> None:
    """Draw a hub using the provided solid `color` for the hub body.

    Non-normal zones receive an outer ring indicating the zone type.
    """
    if hub.zone == Zones.RESTRICTED:
        colore = YELLOW
    elif hub.zone == Zones.PRIORITY:
        colore = GREEN
    elif hub.zone == Zones.NORMAL:
        colore = WHITE
    else:
        colore = RED
    if hub.zone != Zones.NORMAL:
        pygame.draw.circle(window, colore,
                           (hub.x*150 + 50, hub.y*150 + 350), 27, 2)
        pygame.draw.circle(window, BACKGROUND,
                           (hub.x*150 + 50, hub.y*150 + 350), 25, 6)
    pygame.draw.circle(window, color,
                       (hub.x*150 + 50, hub.y*150 + 350), 20)
    text = font.render(f"{hub.name}", True, WHITE)
    center_text = text.get_rect(center=(hub.x*150 + 50, hub.y*150 + 385))
    window.blit(text, center_text)


def draw_connect(ope: Operate, window: Surface) -> None:
    """Draw all connection lines between hubs for the current network.

    Lines are drawn in `GREY` connecting hub centers according to the
    network `connections` list.
    """
    for conect in ope.simul._net.connections:
        hub1 = ope.simul._net.hub_by_name[conect.name_first_hub]
        hub2 = ope.simul._net.hub_by_name[conect.name_second_hub]
        poit1 = (hub1.x*150 + 50, hub1.y*150 + 350)
        poit2 = (hub2.x*150 + 50, hub2.y*150 + 350)
        pygame.draw.line(window, GREY, poit1, poit2)


def redraw_net(ope: Operate, window: Surface, times: float) -> None:
    """Clear the window and draw connections and hubs for a fresh frame.

    This is the base drawing pass used by the drone rendering helpers.
    """
    window.fill((30, 30, 30))
    draw_connect(ope, window)
    draw_hubs(ope, window, times)


def draw_drones(drones: list[Drones_pos], ope: Operate,
                windows: Surface, times: float,
                moves: bool) -> None:
    """Draw drones: either static positions or animate moving drones.

    If `moves` is True the function identifies moving drones and
    triggers the movement animation, otherwise drones are rendered at
    their current positions.
    """
    redraw_net(ope, windows, times)
    if moves:
        movement = [move for move in drones
                    if move.pre_hub != move.drone.hub
                    or move.drone.in_air
                    or move.pre_in_air != move.drone.in_air]
        wait_in_air = [move for move in drones if move.drone.in_air]
        stay = [move for move in drones if move not in movement]
        if len(movement) != 0:
            for move in movement:
                if move in wait_in_air:
                    move.set__future_pos(True)
                else:
                    move.set__future_pos()
            draw_movenent(ope, windows, stay, movement, times)
    else:
        for dron in drones:
            __draw_dron(windows, dron.drone, dron.x, dron.y)
    pygame.display.flip()


def __draw_dron(window: Surface, dron: Drones, x: int, y: int) -> None:
    """Draw a single drone marker with its identifier text.

    A circular marker and a text label `D{id}` are drawn at (x,y).
    """
    pygame.draw.circle(window, GREY, (x, y), 15)
    text = font.render(f"D{dron.id}", True, WHITE)
    center_text = text.get_rect(center=(x, y))
    window.blit(text, center_text)


def draw_movenent(ope: Operate, window: Surface, stay: list[Drones_pos],
                  move: list[Drones_pos], times: float) -> None:
    """Animate drones that are moving between hubs over several frames.

    The function interpolates drone positions over a fixed number of
    frames and renders intermediate positions to create smooth motion.
    """
    num = 50
    for n in range(1, num + 1):
        progress = n / num
        redraw_wait(ope, window, stay, times)
        for mov in move:
            fut_x, fut_y = mov.get__future_pos()
            fut_x = int(mov.x + (fut_x - mov.x) * progress)
            fut_y = int(mov.y + (fut_y - mov.y) * progress)
            __draw_dron(window, mov.drone, fut_x, fut_y)
        pygame.display.flip()
        pygame.time.delay(5)
    for mov in move:
        mov.x, mov.y = mov.get__future_pos()
        if not mov.drone.in_air:
            mov.pre_hub = mov.drone.hub


def redraw_wait(ope: Operate, pantalla: Surface,
                stay: list[Drones_pos], times: float) -> None:
    """Draw the network and all drones that are currently waiting.

    Stationary drones are rendered on top of the network background.
    """
    redraw_net(ope, pantalla, times)
    for dron in stay:
        __draw_dron(pantalla, dron.drone, dron.x, dron.y)
