import pygame
import ScreenManager
import PlayerManager
import EventManager
import MenuManager

class DelayTime :
    INFINITE = -1
    MIN = 60000
    SEC = 1000
"""
    해당 프로그램에서는 밀리초를 사용하는데
    1 초는 1000 밀리초이다.
    하지만 이 코드에서 deltaTime 은 밀리초 / 10 을 사용하므로
    deltaTime 1 당 10 밀리초가 된다.
    그러므로 1초(SEC) 동안의 deltaTime 은 1000 에서 10 을 나눈 100이 된다.
"""

class KeyState :
    def __init__(self) :
        self.left : bool = False
        self.right : bool = False
        self.up : bool = False
        self.down : bool = False

        self.e : bool = False
        self.j : bool = False
        self.k : bool = False
        self.l : bool = False

        self.space : bool = False
        self.lshift : bool = False

        self.esc : bool = False
        
        self.mouseLeft : bool = False
        self.mouseRight : bool = False

    def isPressedXAxis(self) :
        if self.left and self.right :
            return False
        else :
            return self.left or self.right

class Setting :
    def __init__(self) :
        self.effectVolume : int = 50
        self.musicVolume : int = 50
        self.screenShake : bool = True
        self.showHPMode : int = 1
        self.fps : int = 60

class Game() :
    class Instance :
        def __init__(self, screenController : ScreenManager.ScreenController, player : PlayerManager.Player) :
            self.__screenController : ScreenManager.ScreenController = screenController
            self.__player : PlayerManager.Player = player
            self.keyState : KeyState = KeyState()
            self.setting = Setting()
            self.settingMenu : MenuManager.SettingMenu = MenuManager.SettingMenu()
            self.endingMenu : MenuManager.EndingMenu = MenuManager.EndingMenu()

            pygame.mouse.set_visible(False)

        def getScreenController(self) :
            return self.__screenController

        def getPlayer(self) :
            return self.__player
        
        def setPlayer(self, player) :
            self.__player = player

        def receiveKeyEvent(self, event) : 
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_a :
                    self.keyState.left = True
                elif event.key == pygame.K_d :
                    self.keyState.right = True
                elif event.key == pygame.K_w :
                    self.keyState.up = True
                elif event.key == pygame.K_s :
                    self.keyState.down = True
                elif event.key == pygame.K_e :
                    self.keyState.e = True
                elif event.key == pygame.K_j :
                    self.keyState.j = True
                elif event.key == pygame.K_k :
                    self.keyState.k = True
                elif event.key == pygame.K_l :
                    self.keyState.l = True
                elif event.key == pygame.K_SPACE :
                    self.keyState.space = True
                elif event.key == pygame.K_LSHIFT :
                    self.keyState.lshift = True
                elif event.key == pygame.K_ESCAPE :
                    self.keyState.esc = True
                    self.__screenController.onSettingMenu = not self.__screenController.onSettingMenu
                    if self.__screenController.onSettingMenu :
                        pygame.mouse.set_visible(True)
                    else :
                        pygame.mouse.set_visible(False)
            
            if event.type == pygame.KEYUP :
                if event.key == pygame.K_a :
                    self.keyState.left = False
                elif event.key == pygame.K_d :
                    self.keyState.right = False
                elif event.key == pygame.K_w :
                    self.keyState.up = False
                elif event.key == pygame.K_s :
                    self.keyState.down = False
                elif event.key == pygame.K_e :
                    self.keyState.e = False
                elif event.key == pygame.K_j :
                    self.keyState.j = False
                elif event.key == pygame.K_k :
                    self.keyState.k = False
                elif event.key == pygame.K_l :
                    self.keyState.l = False
                elif event.key == pygame.K_SPACE :
                    self.keyState.space = False
                elif event.key == pygame.K_LSHIFT :
                    self.keyState.lshift = False
                elif event.key == pygame.K_ESCAPE :
                    self.keyState.esc = False

            if event.type == pygame.MOUSEBUTTONDOWN :
                if event.button == 1 :
                    self.keyState.mouseLeft = True
                elif event.button == 2 :
                    self.keyState.mouseRight = True

            if event.type == pygame.MOUSEBUTTONUP :
                if event.button == 1 :
                    self.keyState.mouseLeft = False
                elif event.button == 2 :
                    self.keyState.mouseRight = False

        def onEntityMoveEvent(self, event : EventManager.EntityMoveEvent) :
            if event.getEntity().moveLock.x :
                if event.getMoveFrom().x != event.getMoveTo().x :
                    event.cancel()
                
            elif event.getEntity().moveLock.y :
                if event.getMoveFrom().y != event.getMoveTo().y :
                    event.cancel()

        def onEntityDamageEvent(self, event : EventManager.EntityDamageEvent) :
            import GameManager
            if event.getEntity().noPain :
                event.cancel()

            if event.getAttacker() == GameManager.Game.getInstance().getPlayer() :
                GameManager.Game.getInstance().getPlayer().setTarget(event.getEntity())

        def onEntityDeathEvent(self, event : EventManager.EntityDeathEvent) :
            pass

        def receiveEvent(self, event : EventManager.Event) :
            if isinstance(event, EventManager.EntityMoveEvent) :
                self.onEntityMoveEvent(event)
            
            elif isinstance(event, EventManager.EntityDamageEvent) :
                self.onEntityDamageEvent(event)

            elif isinstance(event, EventManager.EntityDeathEvent) :
                self.onEntityDeathEvent(event)
    
    @classmethod
    def init(cls, screenController : ScreenManager.ScreenController, player : PlayerManager.Player) :
        if hasattr(cls, 'instance') :
            return
        else :
            cls.instance = cls.Instance(screenController, player)

    @classmethod
    def getInstance(cls) :
        if not hasattr(cls, 'instance') :
            return None
        else :
            return cls.instance