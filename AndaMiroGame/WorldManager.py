import random
import pygame

class World() :
    def __init__(self) :
        import BlockManager
        import EntityManager
        import ParticleManager
        import PlayerManager
        import NpcManager
        self.__blockEntities : list[BlockManager.Block] = []
        self.__npcEntities : list[NpcManager.Npc] = []
        self.__livingEntities : list[EntityManager.Living] = []
        self.__particleEntities : list[ParticleManager.Particle]  = []
        self.__playerEntity : list[PlayerManager.Player] = []
        self.isOnline = False
        self.isClear = False
        self.playTime = 0

    def drawBackGround(self) :
        import GameManager
        resolution = pygame.display.get_window_size()
        GameManager.Game.getInstance().getScreenController().screen.fill((0, 0, 0), pygame.Rect(0, 0, resolution[0], resolution[1]))

    def addEntity(self, entity) :
        import BlockManager
        import EntityManager
        import ParticleManager
        import PlayerManager
        import NpcManager
        if isinstance(entity, BlockManager.Block) :
            self.__blockEntities.append(entity)

        elif isinstance(entity, PlayerManager.Player) :
            for player in self.__playerEntity :
                player.setWorld(None)

            self.__playerEntity.clear()
            self.__playerEntity.append(entity)

        elif isinstance(entity, NpcManager.Npc) :
            self.__npcEntities.append(entity)
        
        elif isinstance(entity, ParticleManager.Particle) :
            self.__particleEntities.append(entity)
            
        elif isinstance(entity, EntityManager.Living) :
            self.__livingEntities.append(entity)

    def removeEntity(self, entity) :
        import BlockManager
        import EntityManager
        import ParticleManager
        import PlayerManager
        import NpcManager
        if isinstance(entity, BlockManager.Block) :
            entity.setWorld(None)
            self.__blockEntities.remove(entity)

        elif isinstance(entity, PlayerManager.Player) :
            entity.setWorld(None)
            self.__playerEntity.remove(entity)
        
        elif isinstance(entity, NpcManager.Npc) :
            self.__npcEntities.remove(entity)

        elif isinstance(entity, ParticleManager.Particle) :
            entity.setWorld(None)
            self.__particleEntities.remove(entity)

        elif isinstance(entity, EntityManager.Living) :
            entity.setWorld(None)
            self.__livingEntities.remove(entity)


    def getBlocks(self) :
        return self.__blockEntities

    def clearBlock(self) :
        for block in self.__blockEntities :
            block.setWorld(None)

        self.__blockEntities.clear()

    def getLivings(self) :
        return self.__livingEntities

    def getAliveLivingCount(self) :
        count = 0
        for living in self.__livingEntities :
            if living.health > 0 :
                count += 1
                
        return count

    def clearLiving(self) : 
        for living in self.__livingEntities :
            living.setWorld(None)

        self.__livingEntities.clear()

    def getParticles(self) :
        return self.__particleEntities

    def clearParticle(self) : 
        for particle in self.__particleEntities :
            particle.setWorld(None)
            
        self.__particleEntities.clear()

    def getNpcs(self) :
        return self.__npcEntities

    def clearNpc(self) : 
        for npc in self.__npcEntities :
            npc.setWorld(None)

        self.__npcEntities.clear()

    def getPlayer(self) :
        return self.__playerEntity

class Stage1(World) :
    def __init__(self) :
        import BlockManager
        import GameManager
        import EntityManager
        import NpcManager
        import ParticleManager
        import EnemyManager
        super().__init__()
        self.__tutorialEntites : list[EntityManager.Entity] = []
        self.__spawnWaitingEntites : list[EntityManager.Entity] = []

# ===== 조작키 설명 섬 =====

        for i in range(-5, 0) :
            block = BlockManager.LongGround(pygame.Vector3(i * 200, 0, 14))
            block.setWorld(self)
            self.__tutorialEntites.append(block)

            block = BlockManager.UnderGround(pygame.Vector3(i * 200, 500, 12))
            block.setWorld(self)
            self.__tutorialEntites.append(block)

            block = BlockManager.UnderGround(pygame.Vector3(i * 200, 1000, 11))
            block.setWorld(self)
            self.__tutorialEntites.append(block)

        for i in range(0, 20) :

            if i >= 11 and i < 15:
                block = BlockManager.LongGround(pygame.Vector3(i * 200, 650 - (i - 11) * 50, 12))
                block.setWorld(self)
                self.__tutorialEntites.append(block)
                continue

            if i >= 15 :
                block = BlockManager.LongGround(pygame.Vector3(i * 200, 0, 14))
                block.setWorld(self)

                block = BlockManager.UnderGround(pygame.Vector3(i * 200, 500, 12))
                block.setWorld(self)

                block = BlockManager.UnderGround(pygame.Vector3(i * 200, 1000, 11))
                block.setWorld(self)
                continue
            
            block = BlockManager.LongGround(pygame.Vector3(i * 200, 700, 12))
            block.setWorld(self)
            self.__tutorialEntites.append(block)
            if random.randint(0, 1) :
                block = BlockManager.Bush(pygame.Vector3(i * 200, 100, 0))
                block.setWorld(self)
                self.__tutorialEntites.append(block)

        block = BlockManager.RedWall(pygame.Vector3(4500, 100, 10))
        block.setWorld(self)
        self.__tutorialEntites.append(block)
        block = BlockManager.RedWall(pygame.Vector3(4500, -900, 10))
        block.setWorld(self)
        self.__tutorialEntites.append(block)

# ===== Npc 생성 =====

        npc = NpcManager.Stage1TpNpc(pygame.Vector3(1400, 150, 10))
        npc.setWorld(self)
        self.__tutorialEntites.append(npc)
        npc = NpcManager.Stage1StartNpc(pygame.Vector3(4100, 150, 10))
        npc.setWorld(self)
        self.__tutorialEntites.append(npc)
        particle = ParticleManager.TextParticle(pygame.Vector3(4400, 0, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '<= 상호작용하여 스테이지를 시작', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(50, 50, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'A\', \'S\', \'D\' 키를 눌러 이동', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(50, 0, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'LShift\' 키를 눌러 슬라이딩', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(700, 0, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'J\' 키를 길게 눌러 폭발 주먹 공격', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(700, -50, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'K\' 키를 (짧게 또는 길게) 눌러 칼 공격', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(700, -100, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'L\' 키를 눌러 패링 (패링 성공시 패링 쿨타임 초기화)', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(2000, -150, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'SpaceBar\' 키를 눌러 점프 또는 더블점프', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(2250, 100, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'점프\' 상태에서 \'W\' 키를 누른 상태로 \'J\' 키를 눌러 아래로 충격파를 발사', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(2500, -500, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'벽에 매달린\' 상태에서 \'W\' 키를 눌러 벽을 등반', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(3300, -700, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '\'떨어지는\' 상태에서 \'S\' 키를 누른 상태로 \'K\' 키를 눌러 내려찍기', (255, 255, 255), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)
        particle = ParticleManager.TextParticle(pygame.Vector3(1700, 0, 1), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), '<= 나무와 상호작용하여 튜토리얼을 건너뛰기', (0, 255, 0), GameManager.DelayTime.MIN * 5, GameManager.DelayTime.SEC * 0.1)
        particle.setWorld(self)
        self.__tutorialEntites.append(particle)

# ===== 1 스테이지 섬 =====

        for i in range(20, 80) :
            if i >= 75 :
                block = BlockManager.LongGround(pygame.Vector3(i * 200, 0, 12))
                block.setWorld(self)

                block = BlockManager.UnderGround(pygame.Vector3(i * 200, 500, 11))
                block.setWorld(self)

                block = BlockManager.UnderGround(pygame.Vector3(i * 200, 1000, 10))
                block.setWorld(self)
                continue

            block = BlockManager.LongGround(pygame.Vector3(i * 200, 700, 11))
            block.setWorld(self)
            if i > 25 and i < 74 :
                if random.randint(0, 1) :
                    block = BlockManager.Tree(pygame.Vector3(i * 200, 100, random.randint(0, 2)))
                    block.setWorld(self)

                if random.randint(0, 1) :
                    block = BlockManager.Bush(pygame.Vector3(i * 200, 100, 0))
                    block.setWorld(self)

                if i == 29 or i == 35 :
                    self.__spawnWaitingEntites.append(EnemyManager.SmallMonster(pygame.Vector3(i * 200, -50, 1), 0.3, 2.5, 200, 0.005, 0.005))
                    
                if i == 50 or i == 57 :
                    self.__spawnWaitingEntites.append(EnemyManager.GunMonster(pygame.Vector3(i * 200, -50, 1), 0.2, 2.5, 200, 0.005, 0.005))

                if i == 65 :
                    self.__spawnWaitingEntites.append(EnemyManager.SwordMonster(pygame.Vector3(i * 200, -50, 1), 0.25, 2.5, 300, 0.005, 0.005))

                if i == 69 :
                    self.__spawnWaitingEntites.append(EnemyManager.RobotBoss(pygame.Vector3(i * 200, -50, 1), 0.1, 2.5, 500, 0.005, 0.005))

        randx = random.randint(25, 30)
        for i in range(randx, randx + 8) :
            block = BlockManager.Ground(pygame.Vector3(i * 200, -200, 0))
            block.setWorld(self)
            if random.randint(0, 1) :
                block = BlockManager.Tree(pygame.Vector3(i * 200, -400, random.randint(0, 2)))
                block.setWorld(self)

            if random.randint(0, 1) :
                block = BlockManager.Bush(pygame.Vector3(i * 200, -400, 0))
                block.setWorld(self)

            if i == randx + 2 or i == randx + 6 :
                self.__spawnWaitingEntites.append(EnemyManager.SmallMonster(pygame.Vector3(i * 200, -500, 1), 0.3, 2.5, 200, 0.005, 0.005))
        
        randx = randx + 8 + random.randint(1, 3)
        for i in range(randx, randx + 11) :
            block = BlockManager.Ground(pygame.Vector3(i * 200, -300, 0))
            block.setWorld(self)
            if random.randint(0, 1) :
                block = BlockManager.Tree(pygame.Vector3(i * 200, -500, random.randint(0, 2)))
                block.setWorld(self)

            if random.randint(0, 1) :
                block = BlockManager.Bush(pygame.Vector3(i * 200, -500, 0))
                block.setWorld(self)

            if i == randx + 2 or i == randx + 6 :
                self.__spawnWaitingEntites.append(EnemyManager.GunMonster(pygame.Vector3(i * 200, -500, 1), 0.2, 2.5, 200, 0.005, 0.005))

        randx = randx + 11 + random.randint(1, 3)
        for i in range(randx, randx + 10) :
            block = BlockManager.Ground(pygame.Vector3(i * 200, -350, 0))
            block.setWorld(self)
            if random.randint(0, 1) :
                block = BlockManager.Tree(pygame.Vector3(i * 200, -550, random.randint(0, 2)))
                block.setWorld(self)

            if random.randint(0, 1) :
                block = BlockManager.Bush(pygame.Vector3(i * 200, -550, 0))
                block.setWorld(self)
            
            if i == randx + 5 :
                self.__spawnWaitingEntites.append(EnemyManager.SwordMonster(pygame.Vector3(i * 200, -550, 1), 0.25, 2.5, 300, 0.005, 0.005))

    def spawnEnemy(self) :
        import EnemyManager
        for spawnWaitingEntity in self.__spawnWaitingEntites :
            spawnWaitingEntity.setWorld(self)
        
        self.isOnline = True

    def clearTutorialEntity(self) :
        for entity in self.__tutorialEntites :
            self.removeEntity(entity)
        
        self.__tutorialEntites.clear()

    def drawBackGround(self) :
        import GameManager
        resolution = pygame.display.get_window_size()
        GameManager.Game.getInstance().getScreenController().screen.fill((84, 105, 127), pygame.Rect(0, 0, resolution[0], resolution[1] / 2))
        GameManager.Game.getInstance().getScreenController().screen.fill((79, 99, 121), pygame.Rect(0, resolution[1] / 2, resolution[0], resolution[1] / 2))