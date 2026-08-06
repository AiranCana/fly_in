import pygame
import os
from pygame import Surface
from generatorData import NetworkFly, Drones, Hub, Operate


turn = 1
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (127, 127, 127)


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
        else:
            hub = self.drone.get_hub_route()
        x = hub.x*150 + 50 - self.x
        y = hub.y*150 + 350 - self.y

        if midel:
            self.__future_x = self.x + x // 2
            self.__future_y = self.y + y // 2
        else:
            self.__future_x = x + self.x
            self.__future_y = y + self.y


def visual(net: NetworkFly) -> None:
    ope: Operate = net.create_Opertor()
    pygame.init()
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    anch = [hub.x for hub in lis]
    alt = [hub.y for hub in lis]
    drones = [Drones_pos(dro, dro.hub) for dro in ope.drones]
    ANCHO = (max(anch) - min(anch)) * 150 + 100
    ALTO = (max(alt) - min(alt)) * 150 + 450
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Mi ventana")
    reloj = pygame.time.Clock()
    corriendo = espera(ope, drones, pantalla, True)
    os.system("cls" if os.name == "nt" else "clear")
    print_animation(ope, drones, pantalla, reloj, corriendo)
    pygame.quit()


def print_animation(ope, drones, pantalla, reloj, corriendo):
    global turn
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                if evento.key in (pygame.K_RIGHT, pygame.K_d):
                    lis: list[int] = ope.order_target()
                    ope.turns(lis, turn)
                    turn += 1
        draw_drone(drones, ope, pantalla)
        if (ope.is_finished()):
            pygame.time.delay(250)
            corriendo = False
        reloj.tick(60)


def espera(ope, drones, pantalla, esperando):
    corriendo = True
    draw_drone(drones, ope, pantalla)
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
                esperando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                    esperando = False
                if evento.key == pygame.K_SPACE:
                    esperando = False
    return corriendo


def draw_hubs(ope: Operate, pantalla: Surface) -> None:
    lis = ope.simul._net.hubs.copy()
    lis.append(ope.simul._net.start_hub)
    lis.append(ope.simul._net.end_hub)
    for hub in lis:
        if hub.color is not None:
            hola = hub.color
            if len(hola) != 0:
                data = hola.strip("m").split(";")
                color = (int(data[-3]), int(data[-2]), int(data[-1]))
            else:
                color = NEGRO
        else:
            color = NEGRO
        draw_hub(pantalla, hub, color)


def draw_hub(pantalla, hub, color):
    pygame.draw.circle(pantalla, BLANCO,
                       (hub.x*150 + 50, hub.y*150 + 350), 23, 4)
    pygame.draw.circle(pantalla, color,
                       (hub.x*150 + 50, hub.y*150 + 350), 20)


def draw_connect(ope: Operate, pantalla: Surface) -> None:
    for conect in ope.simul._net.connections:
        hub1 = ope.simul._net.hub_by_name[conect.name_first_hub]
        hub2 = ope.simul._net.hub_by_name[conect.name_second_hub]
        poit1 = (hub1.x*150 + 50, hub1.y*150 + 350)
        poit2 = (hub2.x*150 + 50, hub2.y*150 + 350)
        pygame.draw.line(pantalla, BLANCO, poit1, poit2)


def redraw_net(ope: Operate, pantalla: Surface) -> None:
    pantalla.fill((30, 30, 30))
    draw_connect(ope, pantalla)
    draw_hubs(ope, pantalla)


def draw_drone(drone: list[Drones_pos], ope: Operate,
               pantalla: Surface) -> None:
    redraw_net(ope, pantalla)
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
        pygame.draw.circle(pantalla, GRIS,
                           (dron.x, dron.y), 15)
    draw_movenent(ope, pantalla, stay, movement)
    pygame.display.flip()


def draw_movenent(ope: Operate, pantalla: Surface,
                  stay: list[Drones_pos], move: list[Drones_pos]) -> None:
    num = 50
    for n in range(1, num + 1):
        progress = n / num
        redraw_wait(ope, pantalla, stay)
        for mov in move:
            fut_x, fut_y = mov.get__future_pos()
            fut_x = int(mov.x + (fut_x - mov.x) * progress)
            fut_y = int(mov.y + (fut_y - mov.y) * progress)
            pygame.draw.circle(pantalla, GRIS,
                               (fut_x, fut_y), 15)
        pygame.display.flip()
    for mov in move:
        mov.x, mov.y = mov.get__future_pos()
        if not mov.drone.in_air:
            mov.pre_hub = mov.drone.hub


def redraw_wait(ope: Operate, pantalla: Surface,
                stay: list[Drones_pos]) -> None:
    redraw_net(ope, pantalla)
    for dron in stay:
        pygame.draw.circle(pantalla, GRIS,
                           (dron.x, dron.y), 15)
