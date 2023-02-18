import pygame
import EventManager

class Entity(pygame.sprite.Sprite) :
    def __init__(self, position : pygame.Vector3, isCollision : bool) :
        super().__init__()
        import WorldManager
        import AnimationManager
        self.position : pygame.Vector3 = position
        self.speedOfTime : float = 1
        self.__world : WorldManager.World = None
        self.animationController : AnimationManager.AnimationController = AnimationManager.AnimationController(self)
        self.image : pygame.Surface = pygame.Surface((0, 0))
        self.rect : pygame.Rect = self.image.get_rect()
        self.isCollision : bool = isCollision

        self.rect.update(position.x, position.y, 0, 0)

    def setSpeedOfTime(self, speedOfTime : float) :
        self.speedOfTime = speedOfTime

    def setWorld(self, world) :
        self.__world = world
        
        if world != None :
            world.addEntity(self)

    def getWorld(self) :
        return self.__world

    def receiveEvent(self, event : EventManager.EntityEvent) :
        pass

    def collision(self, entity) :
        pass

    def update(self, deltaTime : float) : 
        self.animationController.update(deltaTime)

class HitBox :
    def __init__(self) :
        self.damageBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.scanBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.leftBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.rightBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.topBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.bottomBox : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.extraBox : pygame.Rect = pygame.Rect(0, 0, 0, 0) # 여분의 히트박스
        self.extraBox2 : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.extraBox3 : pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.left : Entity = None
        self.right : Entity = None
        self.top : Entity = None
        self.bottom : Entity = None
        self.extra : Entity = None
        self.extra2 : Entity = None
        self.extra3 : Entity = None

    def clear(self) :
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.extra = None
        self.extra2 = None
        self.extra3 = None

    def clearExtra(self) :
        self.extra = None
        self.extra2 = None
        self.extra3 = None

class Living(Entity) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float, isCollision : bool = True) :
        super().__init__(position, isCollision)
        self.jumpPower : float = jumpPower
        self.health : int = health
        self.maxHealth : int = health
        self.damage : int = 3
        self.noPain = False
        self.multipleSpeed : float = 1
        self.moveDir : pygame.Vector2 = pygame.Vector2(0, 0)
        self.moveLock : pygame.Vector2 = pygame.Vector2(False, False)
        self.viewHitbox : bool = False
        self.hitbox : HitBox = HitBox()
        self.__airResistance : float = airResistance
        self.__gravity : float = gravity
        self.__currentSpeed : float = defaultSpeed
        self.updateHitbox()
    
    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.scanBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (0, 0, 255), self.hitbox.damageBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 0, 0), self.hitbox.leftBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 0, 0), self.hitbox.rightBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (0, 255, 0), self.hitbox.topBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (0, 255, 0), self.hitbox.bottomBox)

    def updateHitbox(self) :
        pass

    def addForce(self, force : pygame.Vector2) :
        self.moveDir += force

    def setForce(self, force : pygame.Vector2) :
        self.moveDir = force

    def isGround(self) :
        return self.hitbox.bottom != None

    def move(self, deltaTime : float) :
        import EventManager
        if self.moveDir.x < 0 :
            self.moveDir.x = min(0, self.moveDir.x + self.__airResistance * deltaTime * self.speedOfTime)

        if self.moveDir.x > 0 : 
            self.moveDir.x = max(0, self.moveDir.x - self.__airResistance * deltaTime * self.speedOfTime)

        if self.moveDir.y != 0 or not self.hitbox.bottom : 
            self.moveDir.y += (self.__gravity + self.__airResistance) * deltaTime * self.speedOfTime
        
        moveTo = pygame.Vector3(self.position)
        self.updateHitbox()
        self.hitbox.clear()
        import WorldManager
        if isinstance(self.getWorld(), WorldManager.World) :
            for other in self.getWorld().getBlocks() : #TODO : Block 외의 다른 오브젝트도 getEntities 함수 추가
                if other.isCollision and pygame.Rect.colliderect(self.hitbox.leftBox, other.rect) :
                    if self.moveDir.x < 0 :
                        self.moveDir.x = 0

                    self.hitbox.left = other
                    other.collision(self)

                if other.isCollision and pygame.Rect.colliderect(self.hitbox.rightBox, other.rect) :
                    if self.moveDir.x > 0 :
                        self.moveDir.x = 0

                    self.hitbox.right = other
                    other.collision(self)

                if other.isCollision and pygame.Rect.colliderect(self.hitbox.topBox, other.rect) :
                    if self.moveDir.y < 0 :
                        self.moveDir.y = 0

                    self.hitbox.top = other
                    other.collision(self)

                if other.isCollision and pygame.Rect.colliderect(self.hitbox.bottomBox, other.rect) :
                    if self.moveDir.y >= 0 and not self.moveLock.y:
                        self.moveDir.y = 0
                        moveTo.y = int(other.position.y - other.rect.height)

                        # Not Used
                        # if not self.moveLock.y and not self.isGround() and int(moveTo.y) > int(other.position.y - other.rect.height) :
                        #     moveTo.y = int(other.position.y - other.rect.height)
                    
                    self.hitbox.bottom = other
                    other.collision(self)

        if not self.moveLock.x :
            moveTo.x += self.moveDir.x * self.__currentSpeed * deltaTime * self.multipleSpeed * self.speedOfTime
        if not self.moveLock.y :
            moveTo.y += self.moveDir.y * deltaTime * self.speedOfTime

        event = EventManager.EntityMoveEvent(self, self.position, moveTo)
        event.call()

        if not event.isCancelled() :
            self.position = moveTo

    def jump(self) :
        self.moveDir.y = -1 * self.jumpPower

    def knockback(self, power : pygame.Vector2) :
        self.moveDir = power

    def death(self, killer) :
        pass

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        pass

    def update(self, deltaTime : float) :
        self.move(deltaTime)
        if self.position.y >= 5000 :
            self.damaged(self, self.health, pygame.Vector2(0, 0))

        super().update(deltaTime)