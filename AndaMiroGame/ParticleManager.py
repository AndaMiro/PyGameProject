import pygame
import EntityManager
import GameManager

class Particle(EntityManager.Entity) :
    def __init__(self, position : pygame.Vector3, lifeTime : int, isCollision : bool = False) :
        super().__init__(position, isCollision)
        self.lifeTime : int = lifeTime
    
    def playParticle(self) :
        self.animationController.playAnimation('particle')

    def update(self, deltaTime: float) :
        if self.animationController.isEnd() and self.lifeTime != GameManager.DelayTime.INFINITE :
            self.lifeTime -= deltaTime

        if self.lifeTime <= 0 :
            self.getWorld().removeEntity(self)
            return

        super().update(deltaTime)

class TextParticle(Particle) :
    def __init__(self, position : pygame.Vector3, font : pygame.font.Font, text : str, color : pygame.Color, lifeTime : int, printDelay : int = 0, oneByOne : bool = False, isRepeat : bool = False) :
        super().__init__(position, lifeTime)
        self.font : pygame.font.Font = font
        self.text : str = text
        self.color : pygame.Color = color
        self.__delayTime : int = printDelay
        self.__printDelay : int = printDelay
        self.__oneByOne : bool = oneByOne
        self.__isRepeat : bool = isRepeat
        self.__currentTextCount : int = 0
        self.__deltaTime : int = 0

    def getSurface(self) :
        return self.font.render(self.text[0 : self.__currentTextCount], False, self.color)

    def update(self, deltaTime : float) : 
        self.__deltaTime += deltaTime
        self.__delayTime -= deltaTime

        if self.__delayTime <= 0 :
            self.__delayTime = self.__printDelay
            if not self.__oneByOne :
                self.__currentTextCount = len(self.text)
            if self.__oneByOne and self.__currentTextCount <= len(self.text) :
                self.__currentTextCount += 1
            
            elif self.__isRepeat :
                if self.__currentTextCount == 0 :
                    self.__currentTextCount = len(self.text)
                else :
                    self.__currentTextCount = 0

        if self.lifeTime != GameManager.DelayTime.INFINITE :
            if self.__oneByOne and self.__deltaTime > len(self.text) * self.__printDelay :
                self.lifeTime -= deltaTime

            elif not self.__oneByOne and self.__deltaTime > self.__printDelay :
                self.lifeTime -= deltaTime

            if self.lifeTime <= 0 and self.__oneByOne and self.__currentTextCount <= len(self.text) :
                self.lifeTime = 1

            if self.lifeTime <= 0 :
                self.getWorld().removeEntity(self)
                return

        if self.lifeTime == GameManager.DelayTime.INFINITE and self.__currentTextCount >= len(self.text) :
            self.__deltaTime = self.__printDelay * len(self.text)

        super().update(deltaTime)

# ===== Dust Particle =====

class DustParticle(Particle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(position, lifeTime)
        self.owner : EntityManager.Entity = owner

class JumpParticle(DustParticle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(owner, position, lifeTime)
        import AnimationManager
        self.animationController.addAnimation(AnimationManager.JumpDust())
        self.setWorld(owner.getWorld())

class LandingParticle(DustParticle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(owner, position, lifeTime)
        import AnimationManager
        self.animationController.addAnimation(AnimationManager.LandingDust())
        self.setWorld(owner.getWorld())

class RunStartParticle(DustParticle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(owner, position, lifeTime)
        import AnimationManager
        self.animationController.addAnimation(AnimationManager.RunStartDust())
        self.setWorld(owner.getWorld())
        self.animationController.flip.x = owner.animationController.flip.x

# ===== AttackParticle =====

class AttackParticle(Particle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(position, lifeTime)
        self.owner = owner

class AirDownPunchParticle(AttackParticle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(owner, position, lifeTime)
        import AnimationManager
        self.animationController.addAnimation(AnimationManager.AirDownPunchDust())
        self.setWorld(owner.getWorld())

class AirSlamParticle(AttackParticle) :
    def __init__(self, owner : EntityManager.Entity, position : pygame.Vector3, lifeTime : int) :
        super().__init__(owner, position, lifeTime)
        import AnimationManager
        self.animationController.addAnimation(AnimationManager.AirSlamDust())
        self.setWorld(owner.getWorld())