import pygame

class ScreenObject :
    def __init__(self, position : pygame.Vector2) :
        self.__position : pygame.Vector2 = position
        self.image : pygame.Surface = pygame.Surface((0, 0))
        self.rect : pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def getPosition(self) : 
        return self.__position

    def update(self) :
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.__position

class ImageLabel(ScreenObject) :
    def __init__(self, position : pygame.Vector2, image : pygame.Surface) :
        super().__init__(position)
        self.image = image

class TextLabel(ScreenObject) :
    def __init__(self, position : pygame.Vector2, font : pygame.font.Font = None, text : str = '', color : pygame.Color = None) :
        super().__init__(position)
        self.__font : pygame.font.Font = font
        self.__text : str = text
        self.__color : pygame.Color = color

        self.image = self.__font.render(self.__text, False, self.__color)

    def setText(self, text : str) :
        self.__text = str(text)
    
    def update(self) :
        self.image = self.__font.render(self.__text, False, self.__color)
        super().update()

class CheckBox(ScreenObject) :
    def __init__(self, position : pygame.Vector2, defaultButtonImg : pygame.Surface, checkButtonImg : pygame.Surface, default : bool = False) :
        super().__init__(position)
        self.__defaultButtonImg : pygame.Surface = defaultButtonImg
        self.__checkButtonImg : pygame.Surface = checkButtonImg
        self.__isChecked : bool = default

        self.image = defaultButtonImg

    def isChecked(self) : 
        return self.__isChecked

    def update(self) :
        import GameManager
        mousePos = pygame.mouse.get_pos()
        if self.rect.left <= mousePos[0] and mousePos[0] <= self.rect.right and self.rect.top <= mousePos[1] and mousePos[1] <= self.rect.bottom :
            if GameManager.Game.getInstance().keyState.mouseLeft :
                self.__isChecked = not self.__isChecked
                GameManager.Game.getInstance().keyState.mouseLeft = False
        
        if self.__isChecked :
            self.image = self.__checkButtonImg
        else :
            self.image = self.__defaultButtonImg

        super().update()

class Button(ScreenObject) :
    def __init__(self, position : pygame.Vector2, defaultButtonImg : pygame.Surface, selectButtonImg : pygame.Surface, action = None) :
        super().__init__(position)
        self.__defaultButtonImg : pygame.Surface = defaultButtonImg
        self.__selectButtonImg : pygame.Surface = selectButtonImg
        self.__action = action
        self.image = defaultButtonImg

    def click(self) :
        if self.__action != None :
            self.__action()

    def update(self) :
        import GameManager
        mousePos = pygame.mouse.get_pos()
        if self.rect.left <= mousePos[0] and mousePos[0] <= self.rect.right and self.rect.top <= mousePos[1] and mousePos[1] <= self.rect.bottom :
            self.image = self.__selectButtonImg
            if GameManager.Game.getInstance().keyState.mouseLeft :
                self.click()
                GameManager.Game.getInstance().keyState.mouseLeft = False
        
        else :
            self.image = self.__defaultButtonImg

        super().update()

class MainMenu :
    def __init__(self) :
        pass

class SettingMenu :
    def __init__(self) :
        resolution = pygame.display.get_window_size()
        self.__screenObjects : dict = {}

        line = pygame.Surface((800, 5))
        line.fill((255, 255, 255))
        self.__screenObjects['line'] = ImageLabel(pygame.Vector2(resolution[0] / 2 - 400, 200), line)
        self.__screenObjects['setting'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 170), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 40), '설정 & 메뉴', (255, 255, 255))

        # Volume
        self.__screenObjects['effectVolumeLabel'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 270), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '효과음', (255, 255, 255))
        self.__screenObjects['effectVolumeDown'] = Button(pygame.Vector2(resolution[0] / 2 + 50, 280), pygame.image.load('Animations\\Ui\\Left.png'), pygame.image.load('Animations\\Ui\\LeftSelected.png'), self.downEffectVolume)
        self.__screenObjects['effectVolumeValue'] = TextLabel(pygame.Vector2(resolution[0] / 2 + 210, 270), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '100', (255, 255, 255))
        self.__screenObjects['effectVolumeUp'] = Button(pygame.Vector2(resolution[0] / 2 + 350, 280), pygame.image.load('Animations\\Ui\\Right.png'), pygame.image.load('Animations\\Ui\\RightSelected.png'), self.upEffectVolume)

        self.__screenObjects['musicVolumeLabel'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 370), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '배경음', (255, 255, 255))
        self.__screenObjects['musicVolumeDown'] = Button(pygame.Vector2(resolution[0] / 2 + 50, 380), pygame.image.load('Animations\\Ui\\Left.png'), pygame.image.load('Animations\\Ui\\LeftSelected.png'), self.downMusicVolume)
        self.__screenObjects['musicVolumeValue'] = TextLabel(pygame.Vector2(resolution[0] / 2 + 210, 370), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '100', (255, 255, 255))
        self.__screenObjects['musicVolumeUp'] = Button(pygame.Vector2(resolution[0] / 2 + 350, 380), pygame.image.load('Animations\\Ui\\Right.png'), pygame.image.load('Animations\\Ui\\RightSelected.png'), self.upMusicVolume)

        # Screen
        self.__screenObjects['screenShakeLabel'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 470), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '화면 흔들림', (255, 255, 255))
        self.__screenObjects['screenShakeValue'] = CheckBox(pygame.Vector2(resolution[0] / 2 + 200, 480), pygame.image.load('Animations\\Ui\\CheckBox.png'), pygame.image.load('Animations\\Ui\\CheckBoxChecked.png'), True)
        
        # Show HP Mode
        self.__screenObjects['showHPModeLabel'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 570), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '체력 표시', (255, 255, 255))
        self.__screenObjects['showHPModeBefore'] = Button(pygame.Vector2(resolution[0] / 2 + 50, 580), pygame.image.load('Animations\\Ui\\Left.png'), pygame.image.load('Animations\\Ui\\LeftSelected.png'), self.beforeShowHPMode)
        self.__screenObjects['showHPModeValue'] = TextLabel(pygame.Vector2(resolution[0] / 2 + 180, 570), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '백분율', (255, 255, 255))
        self.__screenObjects['showHPModeNext'] = Button(pygame.Vector2(resolution[0] / 2 + 350, 580), pygame.image.load('Animations\\Ui\\Right.png'), pygame.image.load('Animations\\Ui\\RightSelected.png'), self.nextShowHPMode)

    def downEffectVolume(self) : 
        import GameManager
        GameManager.Game.getInstance().setting.effectVolume = max(0, GameManager.Game.getInstance().setting.effectVolume - 5)
    
    def upEffectVolume(self) :
        import GameManager
        GameManager.Game.getInstance().setting.effectVolume = min(100, GameManager.Game.getInstance().setting.effectVolume + 5)

    def downMusicVolume(self) : 
        import GameManager
        GameManager.Game.getInstance().setting.musicVolume = max(0, GameManager.Game.getInstance().setting.musicVolume - 5)
    
    def upMusicVolume(self) :
        import GameManager
        GameManager.Game.getInstance().setting.musicVolume = min(100, GameManager.Game.getInstance().setting.musicVolume + 5)

    def beforeShowHPMode(self) :
        import GameManager
        GameManager.Game.getInstance().setting.showHPMode = max(0, GameManager.Game.getInstance().setting.showHPMode - 1)

    def nextShowHPMode(self) :
        import GameManager
        GameManager.Game.getInstance().setting.showHPMode = min(1, GameManager.Game.getInstance().setting.showHPMode + 1)

    def update(self) :
        import GameManager
        self.__screenObjects['effectVolumeValue'].setText(GameManager.Game.getInstance().setting.effectVolume)
        self.__screenObjects['musicVolumeValue'].setText(GameManager.Game.getInstance().setting.musicVolume)
        if GameManager.Game.getInstance().setting.showHPMode == 0 :
            self.__screenObjects['showHPModeValue'].setText('십진법')
        
        else :
            self.__screenObjects['showHPModeValue'].setText('백분율')

        GameManager.Game.getInstance().setting.screenShake = self.__screenObjects['screenShakeValue'].isChecked()

        resolution = pygame.display.get_window_size()
        GameManager.Game.getInstance().getScreenController().screen.fill((0, 0, 0), pygame.Rect(0, 0, resolution[0], resolution[1]))
        for key, object in self.__screenObjects.items() :
            object.update()
            GameManager.Game.getInstance().getScreenController().screen.blit(object.image, object.rect.topleft)

class EndingMenu :
    def __init__(self) :
        resolution = pygame.display.get_window_size()
        self.__screenObjects : dict = {}
        self.isQuit = False
        line = pygame.Surface((800, 5))
        line.fill((255, 255, 255))
        self.__screenObjects['line'] = ImageLabel(pygame.Vector2(resolution[0] / 2 - 400, 200), line)
        self.__screenObjects['clear'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 170), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 40), '클리어!', (255, 255, 255))

        self.__screenObjects['playTime'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 270), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '소요 시간 : ', (255, 255, 255))
        self.__screenObjects['damage'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 370), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '입은 데미지 : ', (255, 255, 255))
        self.__screenObjects['ThanksForPlaying'] = TextLabel(pygame.Vector2(resolution[0] / 2 - 400, 570), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '플레이 해주셔서 감사합니다. (ESC 키를 눌러 게임을 종료)', (255, 255, 255))

    def downEffectVolume(self) : 
        import GameManager
        GameManager.Game.getInstance().setting.effectVolume = max(0, GameManager.Game.getInstance().setting.effectVolume - 5)

    def update(self) :
        import GameManager
        if GameManager.Game.getInstance().keyState.esc :
            pygame.quit()
            self.isQuit = True
            return

        player = GameManager.Game.getInstance().getPlayer()
        self.__screenObjects['playTime'].setText('소요 시간 : ' + str(round(player.getWorld().playTime / 1000, 1)) + '초')
        self.__screenObjects['damage'].setText('입은 데미지 : ' + str(player.maxHealth - player.health) + '데미지')

        resolution = pygame.display.get_window_size()
        GameManager.Game.getInstance().getScreenController().screen.fill((0, 0, 0), pygame.Rect(0, 0, resolution[0], resolution[1]))
        for key, object in self.__screenObjects.items() :
            object.update()
            GameManager.Game.getInstance().getScreenController().screen.blit(object.image, object.rect.topleft)