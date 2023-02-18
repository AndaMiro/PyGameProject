import pygame

def playSound(filename : str) :
    import GameManager
    sound = pygame.mixer.Sound('Sounds\\' + filename)
    sound.set_volume(GameManager.Game.getInstance().setting.effectVolume / 100)
    sound.play()