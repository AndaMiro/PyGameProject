import pygame
import GameManager
import PlayerManager
import WorldManager
import ScreenManager

pygame.init()

world = WorldManager.Stage1()
player = PlayerManager.Player(pygame.Vector3(300, -550, 1), 0.7, 2, 50, 0.005, 0.005)
player.setWorld(world)
#player.viewHitbox = True

GameManager.Game.init(ScreenManager.ScreenController('AndaMiro', 150), player)
game = GameManager.Game.getInstance()
game.getScreenController().setWorld(world)

game.getPlayer().animationController.waitAnimation('run', True)

while True :
    if GameManager.Game.getInstance().endingMenu.isQuit :
        exit()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            pass

        game.receiveKeyEvent(event)

    game.getScreenController().update()