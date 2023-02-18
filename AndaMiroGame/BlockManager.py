import pygame
import EntityManager

class Block(EntityManager.Entity) :
    def __init__(self, position : pygame.Vector3, isCollision : bool = True) :
        super().__init__(position, isCollision)

class RedWall(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\RedWall.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class Bush(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position, False)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\Bush.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class Tree(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position, False)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\Tree.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class Ground(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\Ground.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class UnderGround(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\UnderGround.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class LongGround(Block) :
    def __init__(self, position : pygame.Vector3) :
        import AnimationManager
        super().__init__(position)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\LongGround.png'], 0.1))
        self.animationController.waitAnimation('block', True)

class LongSideGround(Block) :
    def __init__(self, position : pygame.Vector3, isLeft : bool) :
        import AnimationManager
        super().__init__(position)
        self.animationController.addAnimation(AnimationManager.createAnimation('block', ['Animations\\Block\\LongSideGround.png'], 0.1))
        self.animationController.waitAnimation('block', True)
        self.animationController.flip.x = isLeft