import pygame
import os
from pygame import Surface
from pygame.time import Clock
from generatorData import NetworkFly, Drones, Hub, Operate, Zones
import colorsys
from time import time


NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (127, 127, 127)
AMARILLA = (255, 255, 0)
BACKGROUND = (25, 25, 25)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
fuente = None


class Drones_pos:

    def __init__(self, drone: Drones, pos: Hub):
        self.drone = drone
        self.x = pos.x*150 + 50
        self.y = pos.y*150 + 350
        self.__future_x = pos.x*150 + 50
        self.__future_y = pos.y*150 + 350
        self.pre_hub = pos

    def get__future_pos(self) -> tuple[int, int]:
        return (self.__future_x, self.__future_y)

    def set__future_pos(self, midel: bool = False) -> None:
        if not midel:
            hub = self.drone.hub
            x = hub.x*150 + 50 - self.x
            y = hub.y*150 + 350 - self.y
            self.__future_x = x + self.x
            self.__future_y = y + self.y
        else:
            hub = self.drone.get_hub_route()
            origen_x = self.pre_hub.x*150 + 50
            origen_y = self.pre_hub.y*150 + 350
            destino_x = hub.x*150 + 50
            destino_y = hub.y*150 + 350
            self.__future_x = origen_x + (destino_x - origen_x) // 2
            self.__future_y = origen_y + (destino_y - origen_y) // 2


def visual(net: NetworkFly) -> None:
    global fuente
    ope: Operate = net.create_Opertor()
    pygame.init()
    fuente = pygame.font.SysFont("Arial", 14, bold=True)
    anch, alt = order_list(ope)
    drones = [Drones_pos(dro, dro.hub) for dro in ope.drones]
    ANCHO = (max(anch) - min(anch)) * 150 + 150
    ALTO = (max(alt) - min(alt)) * 150 + 450
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Mi ventana")
    reloj = pygame.time.Clock()
    corriendo = True
    os.system("cls" if os.name == "nt" else "clear")
    print_animation(ope, drones, pantalla, reloj, corriendo)
    pygame.quit()


def order_list(ope: Operate) -> tuple[list[int], list[int]]:
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    anch = [hub.x for hub in lis]
    alt = [hub.y for hub in lis]
    return anch, alt


def print_animation(
        ope: Operate,
        drones: list[Drones_pos],
        pantalla: Surface,
        reloj: Clock,
        corriendo: bool) -> None:
    times = time()
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                if evento.key in (pygame.K_RIGHT, pygame.K_d):
                    lis: list[int] = ope.order_target()
                    ope.turns(lis)
        draw_drones(drones, ope, pantalla, times)
        if (ope.is_finished()):
            pygame.time.delay(250)
            corriendo = False
        reloj.tick(60)


def draw_hubs(ope: Operate, pantalla: Surface, times: float) -> None:
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    for hub in lis:
        if hub.color is not None:
            hola = hub.color
            if len(hola) != 0:
                data = hola.strip("m").split(";")
                color = (int(data[-3]), int(data[-2]), int(data[-1]))
                draw_hub(pantalla, hub, color)
            else:
                draw_hub_rainbow(pantalla, hub, times)
        else:
            draw_hub_rainbow(pantalla, hub, times)


def draw_hub_rainbow(pantalla: Surface, hub: Hub, times: float) -> None:
    if hub.zone == Zones.RESTRICTED:
        colore = AMARILLA
    elif hub.zone == Zones.PRIORITY:
        colore = VERDE
    elif hub.zone == Zones.NORMAL:
        colore = BLANCO
    else:
        colore = ROJO
    if hub.zone != Zones.NORMAL:
        pygame.draw.circle(pantalla, colore,
                           (hub.x*150 + 50, hub.y*150 + 350), 27, 4)
        pygame.draw.circle(pantalla, BACKGROUND,
                           (hub.x*150 + 50, hub.y*150 + 350), 23, 4)
    tiempo_transcurrido = time() - times
    offset = (tiempo_transcurrido * 0.15) % 1.0

    for r in range(20, 0, -1):
        hue = (r / 20 + offset) % 1.0
        r_col, g_col, b_col = colorsys.hsv_to_rgb(hue, 1, 1)
        color = (int(r_col * 255), int(g_col * 255), int(b_col * 255))
        pygame.draw.circle(pantalla, color,
                           (hub.x*150 + 50, hub.y*150 + 350), r)
    text = fuente.render(f"{hub.name}", True, BLANCO)
    center_text = text.get_rect(center=(hub.x*150 + 50, hub.y*150 + 385))
    pantalla.blit(text, center_text)


def draw_hub(pantalla: Surface, hub: Hub, color: tuple[int, int, int]) -> None:
    if hub.zone == Zones.RESTRICTED:
        colore = AMARILLA
    elif hub.zone == Zones.PRIORITY:
        colore = VERDE
    elif hub.zone == Zones.NORMAL:
        colore = BLANCO
    else:
        colore = ROJO
    if hub.zone != Zones.NORMAL:
        pygame.draw.circle(pantalla, colore,
                           (hub.x*150 + 50, hub.y*150 + 350), 27, 2)
        pygame.draw.circle(pantalla, BACKGROUND,
                           (hub.x*150 + 50, hub.y*150 + 350), 25, 6)
    pygame.draw.circle(pantalla, color,
                       (hub.x*150 + 50, hub.y*150 + 350), 20)
    text = fuente.render(f"{hub.name}", True, BLANCO)
    center_text = text.get_rect(center=(hub.x*150 + 50, hub.y*150 + 385))
    pantalla.blit(text, center_text)


def draw_connect(ope: Operate, pantalla: Surface) -> None:
    for conect in ope.simul._net.connections:
        hub1 = ope.simul._net.hub_by_name[conect.name_first_hub]
        hub2 = ope.simul._net.hub_by_name[conect.name_second_hub]
        poit1 = (hub1.x*150 + 50, hub1.y*150 + 350)
        poit2 = (hub2.x*150 + 50, hub2.y*150 + 350)
        pygame.draw.line(pantalla, BLANCO, poit1, poit2)


def redraw_net(ope: Operate, pantalla: Surface, times: float) -> None:
    pantalla.fill((30, 30, 30))
    draw_connect(ope, pantalla)
    draw_hubs(ope, pantalla, times)


def draw_drones(drone: list[Drones_pos], ope: Operate,
                pantalla: Surface, times: float) -> None:
    redraw_net(ope, pantalla, times)
    movement = [move for move in drone
                if move.pre_hub != move.drone.hub or move.drone.in_air]
    wait_in_air = [move for move in drone if move.drone.in_air]
    stay = [move for move in drone if move not in movement]
    if len(movement) != 0:
        for move in movement:
            if move in wait_in_air:
                move.set__future_pos(True)
            else:
                move.set__future_pos()
    for dron in stay:
        __draw_dron(pantalla, dron.drone, dron.x, dron.y)
    draw_movenent(ope, pantalla, stay, movement, times)
    pygame.display.flip()


def __draw_dron(pantalla: Surface, dron: Drones, x: int, y: int) -> None:
    pygame.draw.circle(pantalla, GRIS, (x, y), 15)
    text = fuente.render(f"D{dron.id}", True, BLANCO)
    center_text = text.get_rect(center=(x, y))
    pantalla.blit(text, center_text)


def draw_movenent(ope: Operate, pantalla: Surface, stay: list[Drones_pos],
                  move: list[Drones_pos], times: float) -> None:
    num = 50
    for n in range(1, num + 1):
        progress = n / num
        redraw_wait(ope, pantalla, stay, times)
        for mov in move:
            fut_x, fut_y = mov.get__future_pos()
            fut_x = int(mov.x + (fut_x - mov.x) * progress)
            fut_y = int(mov.y + (fut_y - mov.y) * progress)
            __draw_dron(pantalla, mov.drone, fut_x, fut_y)
        pygame.display.flip()
        pygame.time.delay(5)
    for mov in move:
        mov.x, mov.y = mov.get__future_pos()
        if not mov.drone.in_air:
            mov.pre_hub = mov.drone.hub


def redraw_wait(ope: Operate, pantalla: Surface,
                stay: list[Drones_pos], times: float) -> None:
    redraw_net(ope, pantalla, times)
    for dron in stay:
        __draw_dron(pantalla, dron.drone, dron.x, dron.y)
