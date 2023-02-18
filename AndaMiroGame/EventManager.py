import pygame

class Event :
    def __init__(self) : 
        self.__cancelled : bool = False

    def cancel(self) :
        self.__cancelled = True

    def isCancelled(self) :
        return self.__cancelled

    def call(self) :
        pass

class EntityEvent(Event) :
    def __init__(self, entity) :
        super().__init__() 
        import EntityManager
        self.__entity : EntityManager.Entity = entity

    def getEntity(self) :
        return self.__entity

    def call(self) :
        import GameManager
        GameManager.Game.getInstance().receiveEvent(self)

class EntityMoveEvent(EntityEvent) :
    def __init__(self, entity, moveFrom : pygame.Vector3, moveTo : pygame.Vector3) :
        super().__init__(entity)
        self.__moveFrom : pygame.Vector3 = moveFrom
        self.__moveTo : pygame.Vector3 = moveTo

    def getMoveFrom(self) :
        return self.__moveFrom
    
    def getMoveTo(self) :
        return self.__moveTo

class EntityDamageEvent(EntityEvent) :
    def __init__(self, entity, attacker, damage : float, knockBack : pygame.Vector2) :
        import EntityManager
        super().__init__(entity)
        self.__attacker : EntityManager.Entity = attacker
        self.__damage : float = damage
        self.__kncokBack : pygame.Vector2 = knockBack

    def getAttacker(self) :
        return self.__attacker

    def getDamage(self) : 
        return self.__damage

    def getKnockBack(self) :
        return self.__kncokBack

    def setDamage(self, damage : float) :
        self.__damage = damage

    def setKnockBack(self, knockBack : pygame.Vector2) :
        self.__kncokBack = knockBack

class EntityDeathEvent(EntityEvent) :
    def __init__(self, entity, killer) :
        import EntityManager
        super().__init__(entity)
        self.__killer : EntityManager.Entity = killer

    def getKiller(self) :
        return self.__killer