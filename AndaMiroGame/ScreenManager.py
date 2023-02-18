import random
import pygame

class Camera :
    def __init__(self, speedCorrection : float) :
        self.target : pygame.Vector2 = pygame.Vector2(0, 0)
        self.position : pygame.Vector2 = pygame.Vector2(0, 0)
        self.offset : pygame.Vector2 = pygame.Vector2(0, 0)
        self.speedCorrection : float = speedCorrection
        self.maxDistanceFromPlayer : float = 40

class ScreenController() : 
    def __init__(self, name : str, fps : int) :
        import WorldManager
        import GameManager
        pygame.display.set_caption(name)
        #self.screen : pygame.Surface = pygame.display.set_mode((1024, 768))
        self.screen : pygame.Surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.fps : int = fps
        self.__clock : pygame.time.Clock = pygame.time.Clock()
        self.__shakeDuration : int = 0
        self.__shakeMagnitude : float = 0
        self.__world : WorldManager.World = None
        self.__changeScreenCoolTime : int = GameManager.DelayTime.SEC * 5
        self.__changeScreenCoolDown : int = self.__changeScreenCoolTime
        self.camera : Camera = Camera(250)
        self.onSettingMenu = False
        self.onEndingMenu = False

    def setResolution(self, resolution : pygame.Vector2) :
        self.screen = pygame.display.set_mode((resolution.x, resolution.y), pygame.FULLSCREEN)

    def shakeScreen(self, duration : int, magnitude : float) :
        import GameManager
        if not GameManager.Game.getInstance().setting.screenShake :
            return
            
        self.__shakeDuration = duration
        self.__shakeMagnitude = magnitude
    
    def setWorld(self, world) :
        self.__world = world

    def getWorld(self) :
        return self.__world

    def update(self) :
        import EntityManager
        import ParticleManager
        import GameManager
        deltaTime = self.__clock.tick(self.fps)

        if GameManager.Game.getInstance().getPlayer().getWorld().isClear :
            self.__changeScreenCoolDown -= deltaTime

        if self.__changeScreenCoolDown <= 0 :
            self.onEndingMenu = True
        
        if self.onEndingMenu :
            pygame.mouse.set_visible(True)
            GameManager.Game.getInstance().endingMenu.update()
            if not GameManager.Game.getInstance().endingMenu.isQuit :
                pygame.display.flip()
            return

        if self.onSettingMenu :
            GameManager.Game.getInstance().settingMenu.update()

        else :
            resolution = pygame.display.get_window_size()
            self.camera.offset = pygame.Vector2(resolution[0] / 2, resolution[1] / 2)

            if deltaTime > 100 : # 게임 창을 마우스로 움직일 땐 self.__clock.tick(self.fps) 이 100을 넘어가는 현상 발생 
                deltaTime = 0

            if self.__shakeDuration > 0 :
                self.__shakeDuration = max(0, self.__shakeDuration - deltaTime)
                self.camera.position.x += random.randint(-1 * self.__shakeMagnitude, self.__shakeMagnitude)
                self.camera.position.y += random.randint(-1 * self.__shakeMagnitude, self.__shakeMagnitude)

            self.camera.position.x += (self.camera.target.x - self.camera.position.x) / self.camera.speedCorrection * deltaTime
            self.camera.position.y += (self.camera.target.y - self.camera.position.y) / self.camera.speedCorrection * deltaTime

            if abs(self.camera.target.x - self.camera.position.x) <= 0.5 :
                self.camera.position.x = self.camera.target.x
            if abs(self.camera.target.y - self.camera.position.y) <= 0.5 :
                self.camera.position.y = self.camera.target.y

            if self.__world != None :
                entities = []
                entities += self.__world.getBlocks()
                entities += self.__world.getLivings()
                entities += self.__world.getNpcs()
                entities += self.__world.getPlayer()

                entities.sort(key = lambda entity : entity.position.z)
                entities.reverse()

                entities += self.__world.getParticles() # 파티클은 항상 제일 위에 그려지게 함

                GameManager.Game.getInstance().getPlayer().getWorld().drawBackGround()
                for entity in entities :
                    if isinstance(entity, EntityManager.Living) and entity.viewHitbox :
                        entity.drawHitbox(self.screen)

                    if isinstance(entity, ParticleManager.TextParticle) :
                        self.screen.blit(entity.getSurface(), entity.rect.topleft)

                    entity.update(deltaTime)
                    self.screen.blit(entity.image, entity.rect.topleft)

# ===== 플레이어 HP UI =====

                player = GameManager.Game.getInstance().getPlayer()
                HpCaseBar = pygame.Surface((resolution[0] / 2, 20))
                HpCaseBar.fill((100, 100, 100))
                self.screen.blit(HpCaseBar, ((resolution[0] / 2) - (HpCaseBar.get_rect().width / 2) , resolution[1] - 70))

                enemyCountLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 20).render('남은 적 : ' + str(player.getWorld().getAliveLivingCount()) + '명', False, pygame.Color(255, 255, 255))
                if player.getWorld().isOnline :
                    self.screen.blit(enemyCountLabel, (20, resolution[1] - 90))

                parryCoolLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 20).render('패링 쿨타임 : ' + str(round(player.parryCoolDown / 1000, 1)) + 's', False, pygame.Color(255, 255, 255))
                self.screen.blit(parryCoolLabel, (20, resolution[1] - 70))

                dodgeCoolLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 20).render('슬라이딩 쿨타임 : ' + str(round(player.dodgeCoolDown / 1000, 1)) + 's', False, pygame.Color(255, 255, 255))
                self.screen.blit(dodgeCoolLabel, (20, resolution[1] - 50))

                hpPercent = max(0, round(player.health / player.maxHealth * 100, 1))
                if hpPercent > 0 :
                    hpBar = pygame.Surface(((resolution[0] / 2) / 100 * hpPercent, 20))
                    hpBar.fill((255, 0, 0))
                    self.screen.blit(hpBar, ((resolution[0] / 2) - (HpCaseBar.get_rect().width / 2) , resolution[1] - 70))

                if GameManager.Game.getInstance().setting.showHPMode == 0 :
                    hpLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render(str(player.maxHealth) + '/' + str(player.health), False, pygame.Color(255, 255, 255))
                    self.screen.blit(hpLabel, ((resolution[0] / 2) - (hpLabel.get_rect().width / 2), resolution[1] - 100))
                    
                else :
                    hpLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render(str(hpPercent) + '%', False, pygame.Color(255, 255, 255))
                    self.screen.blit(hpLabel, ((resolution[0] / 2) - (hpLabel.get_rect().width / 2), resolution[1] - 100))

# ===== 적 HP UI =====

                target = GameManager.Game.getInstance().getPlayer().getTarget()
                if target != None :
                    targetHpCaseBar = pygame.Surface((resolution[0] / 2, 20))
                    targetHpCaseBar.fill((100, 100, 100))
                    self.screen.blit(targetHpCaseBar, ((resolution[0] / 2) - (targetHpCaseBar.get_rect().width / 2) , 70))

                    targethpPercent = max(0, round(target.health / target.maxHealth * 100, 1))
                    if targethpPercent > 0 :
                        hpBar = pygame.Surface(((resolution[0] / 2) / 100 * targethpPercent, 20))
                        hpBar.fill((0, 255, 0))
                        self.screen.blit(hpBar, ((resolution[0] / 2) - (targetHpCaseBar.get_rect().width / 2) , 70))

                    targetNameLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render(str(target.getName()), False, pygame.Color(255, 255, 255))
                    self.screen.blit(targetNameLabel, ((resolution[0] / 2) - (targetNameLabel.get_rect().width / 2), 30))

                    targetDamageLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render('공격력 : ' + str(target.damage), False, pygame.Color(255, 255, 255))
                    self.screen.blit(targetDamageLabel, ((resolution[0] / 2) - (targetHpCaseBar.get_rect().width / 2), 100))

                    if GameManager.Game.getInstance().setting.showHPMode == 0 :
                        targetHPLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render('체력 : ' + str(target.maxHealth) + '/' + str(target.health), False, pygame.Color(255, 255, 255))
                        self.screen.blit(targetHPLabel, ((resolution[0] / 2) - (targetHpCaseBar.get_rect().width / 2), 150))
                    
                    else :
                        targetHPLabel = pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30).render('체력 : ' + str(targethpPercent) + '%', False, pygame.Color(255, 255, 255))
                        self.screen.blit(targetHPLabel, ((resolution[0] / 2) - (targetHpCaseBar.get_rect().width / 2), 150))

        #pygame.display.update(sprites)
        pygame.display.flip()