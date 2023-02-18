import pygame
import EntityManager

class Npc(EntityManager.Entity) :
    def __init__(self, position : pygame.Vector2, isCollision : bool = False) :
        super().__init__(position, isCollision)

    def interact(self) : 
        pass

    def update(self, deltaTime : float) :
        super().update(deltaTime)

class Stage1TpNpc(Npc) :
    def __init__(self, position : pygame.Vector2) :
        import AnimationManager
        super().__init__(position, False)
        self.animationController.addAnimation(AnimationManager.Stage1TpNpcIdle())
        self.animationController.addAnimation(AnimationManager.Stage1TpNpcCollision())

    def interact(self) : 
        import GameManager
        GameManager.Game.getInstance().getPlayer().position.update(4000, -100, GameManager.Game.getInstance().getPlayer().position.z)

    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        if pygame.Rect.colliderect(self.rect, GameManager.Game.getInstance().getPlayer().rect) :
            if self.animationController.getCurrentAnimation().name != 'collision' :
                self.animationController.playAnimation('collision', True, True)
            
            if GameManager.Game.getInstance().keyState.e :
                self.interact()
                GameManager.Game.getInstance().keyState.e = False
            
        else :
            if self.animationController.getCurrentAnimation().name == 'collision' :
                self.animationController.playAnimation('idle', True, True)

        super().update(deltaTime)

class Stage1StartNpc(Npc) :
    def __init__(self, position : pygame.Vector2) :
        import AnimationManager
        super().__init__(position, False)
        self.animationController.addAnimation(AnimationManager.Stage1TpNpcIdle())
        self.animationController.addAnimation(AnimationManager.Stage1TpNpcCollision())

    def interact(self) : 
        self.getWorld().clearTutorialEntity()
        self.getWorld().spawnEnemy()

    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        if pygame.Rect.colliderect(self.rect, GameManager.Game.getInstance().getPlayer().rect) :
            if self.animationController.getCurrentAnimation().name != 'collision' :
                self.animationController.playAnimation('collision', True, True)
            
            if GameManager.Game.getInstance().keyState.e :
                self.interact()
                GameManager.Game.getInstance().keyState.e = False
            
        else :
            if self.animationController.getCurrentAnimation().name == 'collision' :
                self.animationController.playAnimation('idle', True, True)

        super().update(deltaTime)