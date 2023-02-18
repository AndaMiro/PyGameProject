import pygame

class Setting :
    def __inti__(self) :
        self.__resolution = pygame.Vector2(1024, 768)
        self.__effectVolume = 100
        self.__musicVolume = 100
        pygame.display.get_window_size()

    def getResolution(self) :
        return self.__resolution

    def getEffectVolume(self) : 
        return self.__effectVolume

    def getMusicVolume(self) :
        return self.__musicVolume

    def setResolution(self, resolution : pygame.Vector2) :
        import GameManager
        self.__resolution = resolution
        GameManager.Game.getInstance().getScreenController().setResolution(resolution)

    def setEffectVolume(self, volume : float) :
        self.__effectVolume = volume

    def setMusicVolume(self, volume : float) :
        self.__musicVolume = volume