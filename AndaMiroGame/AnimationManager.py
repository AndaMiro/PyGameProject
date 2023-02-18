import pygame

class Animation :
    def __init__(self, name : str, sprites : list[pygame.sprite.Sprite], speed : float) :
        self.name : str = name
        self.sprites : list[pygame.sprite.Sprite] = sprites
        self.speed : float = speed

    def update(self, entity) :
        pass

    def onPlay(self, entity, current_animation_index : int) :
        pass

def createAnimation(name : str, sprite_img_paths : list[str], speed : float) :
    sprites = []
    for img_path in sprite_img_paths :
        sprites.append(pygame.image.load(img_path))        
    return Animation(name, sprites, speed)
    
class AnimationController :
    def __init__(self, entity) :
        import EntityManager
        self.entity : EntityManager.Entity = entity
        self.multipleSpeed : float = 1
        self.flip : pygame.Vector2 = pygame.Vector2(0, 0)
        self.__current_animation : Animation = None
        self.__animations : dict = {}
        self.__repeat : bool = False
        self.__waitingQueue : list[dict] = []
        self.__current_animation_index : float = 0
        self.__current_animation_length : int = 0
        self.__isEnd : bool = True
        self.__deltaTime : int = 0

    def isEnd(self) :
        return self.__isEnd

    def getCurrentAnimation(self) :
        return self.__current_animation

    def getCurrentIndex(self) :
        return int(self.__current_animation_index)

    def addAnimation(self, animation : Animation) :
        if animation.name in self.__animations :
            return False
        else :
            self.__animations[animation.name] = animation
            return True

    def playAnimation(self, name : str, force : bool = False, repeat : bool = False, multipleSpeed : float = 1) : 
        if name not in self.__animations :
            return False
            
        if force :
            self.__repeat = repeat
            self.multipleSpeed = multipleSpeed
            self.__current_animation = self.__animations[name]
            self.__current_animation_index = 0
            self.__current_animation_length = len(self.__current_animation.sprites)
            self.__isEnd = False
            return True

        elif self.__current_animation != None :
            return False

        else :
            self.__repeat = repeat
            self.multipleSpeed = multipleSpeed
            self.__current_animation = self.__animations[name]
            self.__current_animation_index = 0
            self.__current_animation_length = len(self.__current_animation.sprites)
            self.__isEnd = False
            return True

    def stopAnimation(self) : 
        self.__repeat = False
        self.multipleSpeed = 1
        self.__current_animation = None
        self.__current_animation_index = 0
        self.__current_animation_length = 0
        self.__isEnd = True

    def waitAnimation(self, name : str, repeat : bool = False, insertFirst : bool = False, multipleSpeed : float = 1) :
        if self.__isEnd or self.__current_animation == None :
            self.playAnimation(name, False, repeat, multipleSpeed)
        elif insertFirst :
            self.__waitingQueue.insert(0, {'Name' : name, 'Repeat' : repeat, 'multipleSpeed' : multipleSpeed})
        else :
            self.__waitingQueue.append({'Name' : name, 'Repeat' : repeat, 'multipleSpeed' : multipleSpeed})

    def clearWaiting(self) :
        self.__waitingQueue.clear()

    def update(self, deltaTime : float) :
        if self.__current_animation != None :
            self.__deltaTime += deltaTime
            if self.__deltaTime > 10 :
                self.__deltaTime = 0
                before_index = self.__current_animation_index
                self.__current_animation_index += self.__current_animation.speed * self.multipleSpeed * self.entity.speedOfTime
                if int(before_index) < int(self.__current_animation_index) :
                    self.__current_animation_index = int(self.__current_animation_index)
                    self.__current_animation.onPlay(self.entity, self.__current_animation_index)
            
            '''
                    1. int(self.__current_animation_index) => (self.__current_animation_length - 1) 로 조건 설정시 마지막 애니메이션이 씹히는 현상이 발견되어
                    2. int(self.__current_animation_index) => self.__current_animation_length 로 수정, 
                    하지만 self.__current_animation_length 는 self.__current_animation.sprites 의 최대 인덱스보다 1이 더 많기 때문에 out of range가 발생
                    int(self.__current_animation_index) >= self.__current_animation_length 조건 충족 시 self.__current_animation_index 를 (self.__current_animation_length - 1) 로 설정
            '''
            if self.__isEnd or int(self.__current_animation_index) >= self.__current_animation_length : 
                if not self.__repeat :
                    if len(self.__waitingQueue) > 0 :
                        queueData = self.__waitingQueue.pop(0)
                        self.__repeat = queueData['Repeat']
                        self.multipleSpeed = queueData['multipleSpeed']
                        self.__current_animation = self.__animations[queueData['Name']]
                        self.__current_animation_index = 0
                        self.__current_animation_length = len(self.__current_animation.sprites)
                        self.__isEnd = False
                
                    else :
                        self.__current_animation_index = self.__current_animation_length - 1
                        self.__isEnd = True
                
                else :
                    self.__current_animation_index %= self.__current_animation_length
            
            image = self.__current_animation.sprites[int(self.__current_animation_index)]
            self.entity.image = pygame.transform.flip(image, bool(self.flip.x), bool(self.flip.y))
            self.entity.rect = self.entity.image.get_rect()
            
        import GameManager
        self.entity.rect.bottomleft = pygame.Vector2(self.entity.position.x, self.entity.position.y) - GameManager.Game.getInstance().getScreenController().camera.position

# ===== Player Animations =====

class PlayerAnimation(Animation) :
    def __init__(self, name : str, sprites : list[pygame.sprite.Sprite], speed : float) :
        super().__init__(name, sprites, speed)

    def update(self, entity) :
        import PlayerManager
        entity = PlayerManager.Player(entity)

class PlayerIdle(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 7) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Idle\\Idle' + str(i) + '.png'))

        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', player_sprites, 0.1)

class PlayerRunStart(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range (1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\RunStart\\RunStart' + str(i) + '.png'))

        except FileNotFoundError as e :
            print('RunStart 파일이 손상되었습니다. ', e)

        super().__init__('run_start', player_sprites, 0.3)

    def onPlay(self, entity, current_animation_index : int) :
        import ParticleManager
        if current_animation_index == 2 :
            particle = ParticleManager.RunStartParticle(entity, pygame.Vector3(entity.position), 1)
            particle.playParticle()
        super().onPlay(entity, current_animation_index)

class PlayerRun(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 9) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Run\\Run' + str(i) + '.png'))

        except FileNotFoundError as e :
            print('Run 파일이 손상되었습니다. ', e)

        super().__init__('run', player_sprites, 0.2)

    def onPlay(self, entity, current_animation_index : int) :
        import SoundManager
        if current_animation_index == 3 or current_animation_index == 7 :
            SoundManager.playSound('Step.wav')
        super().onPlay(entity, current_animation_index)

class PlayerJump(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 5) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Jump\\Jump' + str(i) + '.png'))

        except FileNotFoundError as e :
            print('Jump 파일이 손상되었습니다. ', e)

        super().__init__('jump', player_sprites, 0.2)

class PlayerFall(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            player_sprites.append(pygame.image.load('Animations\\Player\\Fall\\Fall.png'))
            
        except FileNotFoundError as e :
            print('Fall 파일이 손상되었습니다. ', e)

        super().__init__('fall', player_sprites, 0.1)

class PlayerLanding(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 6) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Landing\\Landing' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Landing 파일이 손상되었습니다. ', e)

        super().__init__('landing', player_sprites, 0.2)

class PlayerWallGrap(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 5) :
                player_sprites.append(pygame.image.load('Animations\\Player\\WallGrap\\WallGrap' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('WallGrap 파일이 손상되었습니다. ', e)

        super().__init__('wall_grap', player_sprites, 0.2)

class PlayerDangle(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            player_sprites.append(pygame.image.load('Animations\\Player\\Dangle\\Dangle.png'))
            
        except FileNotFoundError as e :
            print('Dangle 파일이 손상되었습니다. ', e)

        super().__init__('dangle', player_sprites, 0.1)

class PlayerWallClimb(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 9) :
                player_sprites.append(pygame.image.load('Animations\\Player\\WallClimb\\WallClimb' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('WallClimb 파일이 손상되었습니다. ', e)

        super().__init__('wall_climb', player_sprites, 0.15)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 6 :
            if entity.animationController.flip.x : 
                entity.position.x = entity.position.x - 48
                entity.position.y = entity.position.y - 92
            else :
                entity.position.x = entity.position.x + 48
                entity.position.y = entity.position.y - 92

        super().onPlay(entity, current_animation_index)

class PlayerDodge(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Dodge\\Dodge' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Dodge 파일이 손상되었습니다. ', e)

        super().__init__('dodge', player_sprites, 0.1)

class PlayerDodgeEnd(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\DodgeEnd\\DodgeEnd' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('DodgeEnd 파일이 손상되었습니다. ', e)

        super().__init__('dodge_end', player_sprites, 0.1)

class PlayerCrouch(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Crouch\\Crouch' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Crouch 파일이 손상되었습니다. ', e)

        super().__init__('crouch', player_sprites, 0.1)

class PlayerStandUp(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\StandUp\\StandUp' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('StandUp 파일이 손상되었습니다. ', e)

        super().__init__('stand_up', player_sprites, 0.1)

class PlayerHurt(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 4) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Hurt\\Hurt' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Hurt 파일이 손상되었습니다. ', e)

        super().__init__('hurt', player_sprites, 0.05)

class PlayerDeath(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 16) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Death\\Death' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Death 파일이 손상되었습니다. ', e)

        super().__init__('death', player_sprites, 0.1)

class PlayerFirstPunch(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 14) :
                player_sprites.append(pygame.image.load('Animations\\Player\\FirstPunch\\FirstPunch' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('FirstPunch 파일이 손상되었습니다. ', e)

        super().__init__('first_punch', player_sprites, 0.4)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 8 :
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    if entity.animationController.flip.x and enemy.hitbox.damageBox.centerx <= entity.rect.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                    elif not entity.animationController.flip.x and entity.rect.centerx < enemy.hitbox.damageBox.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))

            GameManager.Game.getInstance().getScreenController().shakeScreen(GameManager.DelayTime.SEC * 0.1, 2)

        elif current_animation_index == 13 :
            GameManager.Game.getInstance().keyState.j = False
        super().onPlay(entity, current_animation_index)

class PlayerSecondPunch(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 14) :
                player_sprites.append(pygame.image.load('Animations\\Player\\SecondPunch\\SecondPunch' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('SecondPunch 파일이 손상되었습니다. ', e)

        super().__init__('second_punch', player_sprites, 0.4)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 8 :
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    if entity.animationController.flip.x and enemy.hitbox.damageBox.centerx <= entity.rect.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                    elif not entity.animationController.flip.x and entity.rect.centerx < enemy.hitbox.damageBox.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))

            GameManager.Game.getInstance().getScreenController().shakeScreen(GameManager.DelayTime.SEC * 0.1, 2)

        elif current_animation_index == 13 :
            GameManager.Game.getInstance().keyState.j = False
        super().onPlay(entity, current_animation_index)

class PlayerFirstSword(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 5) :
                player_sprites.append(pygame.image.load('Animations\\Player\\FirstSword\\FirstSword' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('FirstSword 파일이 손상되었습니다. ', e)

        super().__init__('first_sword', player_sprites, 0.2)

    def onPlay(self, entity, current_animation_index : int) :
        import SoundManager
        if current_animation_index == 1 :
            SoundManager.playSound('Swing.wav')
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    if entity.animationController.flip.x and enemy.hitbox.damageBox.centerx <= entity.rect.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                    elif not entity.animationController.flip.x and entity.rect.centerx < enemy.hitbox.damageBox.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class PlayerSecondSword(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 5) :
                player_sprites.append(pygame.image.load('Animations\\Player\\SecondSword\\SecondSword' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('SecondSword 파일이 손상되었습니다. ', e)

        super().__init__('second_sword', player_sprites, 0.2)

    def onPlay(self, entity, current_animation_index : int) :
        import SoundManager
        if current_animation_index == 1 :
            SoundManager.playSound('Swing.wav')
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    if entity.animationController.flip.x and enemy.hitbox.damageBox.centerx <= entity.rect.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                    elif not entity.animationController.flip.x and entity.rect.centerx < enemy.hitbox.damageBox.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class PlayerThirdSword(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 7) :
                player_sprites.append(pygame.image.load('Animations\\Player\\ThirdSword\\ThirdSword' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('ThirdSword 파일이 손상되었습니다. ', e)

        super().__init__('third_sword', player_sprites, 0.2)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        import SoundManager
        if current_animation_index == 1 :
            SoundManager.playSound('Swing.wav')
            SoundManager.playSound('Explosion.wav')
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    if entity.animationController.flip.x and enemy.hitbox.damageBox.centerx <= entity.rect.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -2))
                
                    elif not entity.animationController.flip.x and entity.rect.centerx < enemy.hitbox.damageBox.centerx :
                        enemy.damaged(entity, entity.damage, pygame.Vector2(2, -2))

        elif current_animation_index == 2 :
            GameManager.Game.getInstance().getScreenController().shakeScreen(GameManager.DelayTime.SEC * 0.5, 2)

        elif current_animation_index == 5 :
            GameManager.Game.getInstance().keyState.k = False

        super().onPlay(entity, current_animation_index)

class PlayerSheathSword(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 4) :
                player_sprites.append(pygame.image.load('Animations\\Player\\SheathSword\\SheathSword' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('SheathSword 파일이 손상되었습니다. ', e)

        super().__init__('sheath_sword', player_sprites, 0.1)

class PlayerAirSlam(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 3) :
                player_sprites.append(pygame.image.load('Animations\\Player\\AirSlam\\AirSlam' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('AirSlam 파일이 손상되었습니다. ', e)

        super().__init__('air_slam', player_sprites, 0.1)

class PlayerAirSlamLanding(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 8) :
                player_sprites.append(pygame.image.load('Animations\\Player\\AirSlamLanding\\AirSlamLanding' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('AirSlamLanding 파일이 손상되었습니다. ', e)

        super().__init__('air_slam_landing', player_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import ParticleManager
        import GameManager
        import SoundManager
        if current_animation_index == 1 :
            SoundManager.playSound('Explosion.wav')
            particle = ParticleManager.AirSlamParticle(entity, pygame.Vector3(entity.position), 1)
            particle.playParticle()
            GameManager.Game.getInstance().getScreenController().shakeScreen(GameManager.DelayTime.SEC * 0.5, 2)

        super().onPlay(entity, current_animation_index)

class PlayerAirDownPunch(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 12) :
                player_sprites.append(pygame.image.load('Animations\\Player\\AirDownPunch\\AirDownPunch' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('AirDownPunch 파일이 손상되었습니다. ', e)

        super().__init__('air_down_punch', player_sprites, 0.3)

    def onPlay(self, entity, current_animation_index : int) :
        import ParticleManager
        import SoundManager
        if current_animation_index == 1 :
            SoundManager.playSound('Explosion.wav')
            particle = ParticleManager.AirDownPunchParticle(entity, pygame.Vector3(entity.position), 1)
            particle.playParticle()
            entity.moveDir.y = -1.3 * entity.jumpPower

        super().onPlay(entity, current_animation_index)

class PlayerParryStance(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 4) :
                player_sprites.append(pygame.image.load('Animations\\Player\\ParryStance\\ParryStance' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('ParryStance 파일이 손상되었습니다. ', e)

        super().__init__('parry_stance', player_sprites, 0.1)

class PlayerParry(PlayerAnimation) :
    def __init__(self) :
        player_sprites = []
        try :
            for i in range(1, 4) :
                player_sprites.append(pygame.image.load('Animations\\Player\\Parry\\Parry' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Parry 파일이 손상되었습니다. ', e)

        super().__init__('parry', player_sprites, 0.1)

# ===== Enemy Animations =====

class EnemyAnimation(Animation) :
    def __init__(self, name : str, sprites : list[pygame.sprite.Sprite], speed : float) :
        super().__init__(name, sprites, speed)

# ===== Small Monster Animations =====

class SmallMonsterIdle(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 7) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SmallMonster\\Idle\\Idle' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', enemy_sprites, 0.1)

class SmallMonsterRun(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 7) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SmallMonster\\Run\\Run' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Run 파일이 손상되었습니다. ', e)

        super().__init__('run', enemy_sprites, 0.1)

class SmallMonsterAttack(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 13) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SmallMonster\\Attack\\Attack' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Attack 파일이 손상되었습니다. ', e)

        super().__init__('attack', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 6 :
            player = GameManager.Game.getInstance().getPlayer()
            if pygame.Rect.colliderect(entity.rect, player.hitbox.damageBox) :
                if entity.animationController.flip.x and player.hitbox.damageBox.centerx <= entity.rect.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                elif not entity.animationController.flip.x and entity.rect.centerx < player.hitbox.damageBox.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class SmallMonsterHurt(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 3) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SmallMonster\\Hurt\\Hurt' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Hurt 파일이 손상되었습니다. ', e)

        super().__init__('hurt', enemy_sprites, 0.05)

class SmallMonsterDeath(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 10) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SmallMonster\\Death\\Death' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Death 파일이 손상되었습니다. ', e)

        super().__init__('death', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 8 :
            entity.getWorld().removeEntity(entity)
            print("Death")

        super().onPlay(entity, current_animation_index)

# ===== Gun Monster Animations =====

class GunMonsterIdle(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Idle\\Idle.png'))
            
        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', enemy_sprites, 0.1)

class GunMonsterWakeUp(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 4) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\WakeUp\\WakeUp' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('WakeUp 파일이 손상되었습니다. ', e)

        super().__init__('wake_up', enemy_sprites, 0.1)

class GunMonsterSleep(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 4) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Sleep\\Sleep' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Sleep 파일이 손상되었습니다. ', e)

        super().__init__('sleep', enemy_sprites, 0.1)

class GunMonsterRun(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 9) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Run\\Run' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Run 파일이 손상되었습니다. ', e)

        super().__init__('run', enemy_sprites, 0.1)

class GunMonsterCharge(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 6) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Charge\\Charge' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Charge 파일이 손상되었습니다. ', e)

        super().__init__('charge', enemy_sprites, 0.1)

class GunMonsterAttack(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 7) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Attack\\Attack' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Attack 파일이 손상되었습니다. ', e)

        super().__init__('attack', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 3 :
            player = GameManager.Game.getInstance().getPlayer()
            if pygame.Rect.colliderect(entity.rect, player.hitbox.damageBox) :
                if entity.animationController.flip.x and player.hitbox.damageBox.centerx <= entity.rect.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                elif not entity.animationController.flip.x and entity.rect.centerx < player.hitbox.damageBox.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)
        
class GunMonsterHurt(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 3) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Hurt\\Hurt' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Hurt 파일이 손상되었습니다. ', e)

        super().__init__('hurt', enemy_sprites, 0.05)

class GunMonsterDeath(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 21) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\GunMonster\\Death\\Death' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Death 파일이 손상되었습니다. ', e)

        super().__init__('death', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 19 :
            entity.getWorld().removeEntity(entity)
            print("Death")

        super().onPlay(entity, current_animation_index)

# ===== Sword Monster Animations =====

class SwordMonsterIdle(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 6) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SwordMonster\\Idle\\Idle' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', enemy_sprites, 0.1)

class SwordMonsterRun(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 9) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SwordMonster\\Run\\Run' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Run 파일이 손상되었습니다. ', e)

        super().__init__('run', enemy_sprites, 0.1)

class SwordMonsterAttack(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 14) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SwordMonster\\Attack\\Attack' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Attack 파일이 손상되었습니다. ', e)

        super().__init__('attack', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 5 or current_animation_index == 9 :
            player = GameManager.Game.getInstance().getPlayer()
            if pygame.Rect.colliderect(entity.rect, player.hitbox.damageBox) :
                if entity.animationController.flip.x and player.hitbox.damageBox.centerx <= entity.rect.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))
                
                elif not entity.animationController.flip.x and entity.rect.centerx < player.hitbox.damageBox.centerx :
                    player.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class SwordMonsterHurt(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 3) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SwordMonster\\Hurt\\Hurt' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Hurt 파일이 손상되었습니다. ', e)

        super().__init__('hurt', enemy_sprites, 0.05)

class SwordMonsterDeath(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 20) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\SwordMonster\\Death\\Death' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Death 파일이 손상되었습니다. ', e)

        super().__init__('death', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 18 :
            entity.getWorld().removeEntity(entity)
            print("Death")

        super().onPlay(entity, current_animation_index)

# ===== Robot Boss Animations =====

class RobotBossIdle(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            enemy_sprites.append(pygame.image.load('Animations\\Enemy\\RobotBoss\\Idle\\Idle.png'))
            
        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', enemy_sprites, 0.1)

class RobotBossRun(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 7) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\RobotBoss\\Run\\Run' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Run 파일이 손상되었습니다. ', e)

        super().__init__('run', enemy_sprites, 0.1)

class RobotBossShield(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 39) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\RobotBoss\\Shield\\Shield' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Shield 파일이 손상되었습니다. ', e)

        super().__init__('shield', enemy_sprites, 0.1)

class RobotBossAttack(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 15) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\RobotBoss\\Attack\\Attack' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Attack 파일이 손상되었습니다. ', e)

        super().__init__('attack', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 5 or current_animation_index == 7 :
            player = GameManager.Game.getInstance().getPlayer()
            if pygame.Rect.colliderect(entity.rect, player.hitbox.damageBox) :
                player.damaged(entity, entity.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class RobotBossDeath(EnemyAnimation) :
    def __init__(self) :
        enemy_sprites = []
        try :
            for i in range(1, 8) :
                enemy_sprites.append(pygame.image.load('Animations\\Enemy\\RobotBoss\\Death\\Death' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('Death 파일이 손상되었습니다. ', e)

        super().__init__('death', enemy_sprites, 0.1)

    def onPlay(self, entity, current_animation_index : int) :
        import GameManager
        if current_animation_index == 3 :
            GameManager.Game.getInstance().getScreenController().shakeScreen(GameManager.DelayTime.SEC * 3, 2)

        super().onPlay(entity, current_animation_index)

# ===== Npc Animations =====

class NpcAnimation(Animation) :
    def __init__(self, name: str, sprites: list[pygame.sprite.Sprite], speed: float) :
        super().__init__(name, sprites, speed)

    def onPlay(self, entity, current_animation_index : int) :
        pass

class Stage1TpNpcIdle(NpcAnimation) :
    def __init__(self) :
        npc_sprites = []
        try :
            npc_sprites.append(pygame.image.load('Animations\\Npc\\Stage1TpNpc\\Idle\\Idle.png'))
            
        except FileNotFoundError as e :
            print('Idle 파일이 손상되었습니다. ', e)

        super().__init__('idle', npc_sprites, 0.1)

class Stage1TpNpcCollision(NpcAnimation) :
    def __init__(self) :
        npc_sprites = []
        try :
            npc_sprites.append(pygame.image.load('Animations\\Npc\\Stage1TpNpc\\Collision\\Collision.png'))
            
        except FileNotFoundError as e :
            print('Collision 파일이 손상되었습니다. ', e)

        super().__init__('collision', npc_sprites, 0.1)

# ===== Particle Animations =====

class ParticleAnimation(Animation) :
    def __init__(self, name: str, sprites: list[pygame.sprite.Sprite], speed: float) :
        super().__init__(name, sprites, speed)

    def onPlay(self, entity, current_animation_index : int) :
        pass

class RunStartDust(ParticleAnimation) :
    def __init__(self) :
        particle_sprites = []
        try :
            for i in range(1, 5) :
                particle_sprites.append(pygame.image.load('Animations\\Particle\\PlayerParticle\\RunStartDust\\RunStartDust' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('RunStartDust 파일이 손상되었습니다. ', e)

        super().__init__('particle', particle_sprites, 0.1)

class LandingDust(ParticleAnimation) :
    def __init__(self) :
        particle_sprites = []
        try :
            for i in range(1, 4) :
                particle_sprites.append(pygame.image.load('Animations\\Particle\\PlayerParticle\\LandingDust\\LandingDust' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('LandingDust 파일이 손상되었습니다. ', e)

        super().__init__('particle', particle_sprites, 0.1)

class JumpDust(ParticleAnimation) :
    def __init__(self) :
        particle_sprites = []
        try :
            for i in range(1, 4) :
                particle_sprites.append(pygame.image.load('Animations\\Particle\\PlayerParticle\\JumpDust\\JumpDust' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('JumpDust 파일이 손상되었습니다. ', e)

        super().__init__('particle', particle_sprites, 0.1)

class AirSlamDust(ParticleAnimation) :
    def __init__(self) :
        particle_sprites = []
        try :
            for i in range(1, 5) :
                particle_sprites.append(pygame.image.load('Animations\\Particle\\PlayerParticle\\AirSlamDust\\AirSlamDust' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('AirSlamDust 파일이 손상되었습니다. ', e)

        super().__init__('particle', particle_sprites, 0.15)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 1 :
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    enemy.damaged(entity.owner, entity.owner.damage, pygame.Vector2(2, -1))

        super().onPlay(entity, current_animation_index)

class AirDownPunchDust(ParticleAnimation) :
    def __init__(self) :
        particle_sprites = []
        try :
            for i in range(1, 6) :
                particle_sprites.append(pygame.image.load('Animations\\Particle\\PlayerParticle\\AirDownPunchDust\\AirDownPunchDust' + str(i) + '.png'))
            
        except FileNotFoundError as e :
            print('AirDownPunchDust 파일이 손상되었습니다. ', e)

        super().__init__('particle', particle_sprites, 0.3)

    def onPlay(self, entity, current_animation_index : int) :
        if current_animation_index == 1 :
            for enemy in entity.getWorld().getLivings() :
                if pygame.Rect.colliderect(entity.rect, enemy.hitbox.damageBox) :
                    enemy.damaged(entity.owner, entity.owner.damage, pygame.Vector2(0, 0))

        super().onPlay(entity, current_animation_index)