import pygame
import EntityManager

class Player(EntityManager.Living) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)
        import AnimationManager
        import EnemyManager
        import GameManager
        self.animationController.addAnimation(AnimationManager.PlayerIdle())
        self.animationController.addAnimation(AnimationManager.PlayerRunStart())
        self.animationController.addAnimation(AnimationManager.PlayerRun())
        self.animationController.addAnimation(AnimationManager.PlayerJump())
        self.animationController.addAnimation(AnimationManager.PlayerFall())
        self.animationController.addAnimation(AnimationManager.PlayerLanding())
        self.animationController.addAnimation(AnimationManager.PlayerWallGrap())
        self.animationController.addAnimation(AnimationManager.PlayerDangle())
        self.animationController.addAnimation(AnimationManager.PlayerWallClimb())
        self.animationController.addAnimation(AnimationManager.PlayerDodge())
        self.animationController.addAnimation(AnimationManager.PlayerDodgeEnd())
        self.animationController.addAnimation(AnimationManager.PlayerCrouch())
        self.animationController.addAnimation(AnimationManager.PlayerStandUp())

        self.animationController.addAnimation(AnimationManager.PlayerHurt())
        self.animationController.addAnimation(AnimationManager.PlayerDeath())

        self.animationController.addAnimation(AnimationManager.PlayerFirstPunch())
        self.animationController.addAnimation(AnimationManager.PlayerSecondPunch())
        self.animationController.addAnimation(AnimationManager.PlayerFirstSword())
        self.animationController.addAnimation(AnimationManager.PlayerSecondSword())
        self.animationController.addAnimation(AnimationManager.PlayerThirdSword())
        self.animationController.addAnimation(AnimationManager.PlayerSheathSword())
        self.animationController.addAnimation(AnimationManager.PlayerAirSlam())
        self.animationController.addAnimation(AnimationManager.PlayerAirSlamLanding())
        self.animationController.addAnimation(AnimationManager.PlayerAirDownPunch())

        self.animationController.addAnimation(AnimationManager.PlayerParryStance())
        self.animationController.addAnimation(AnimationManager.PlayerParry())

        self.__punchMotion : int = 0
        self.__swordMotion : int = 0
        self.maxJumpCount : int = 2
        self.currentJumpCount : int = 0
        self.lastHeight : float = 0
        self.parryCoolDown : int = 0
        self.__parryCoolTime : int = GameManager.DelayTime.SEC * 5
        self.dodgeCoolDown : int = 0
        self.__dodgeCoolTime : int = GameManager.DelayTime.SEC * 3
        self.__target : EnemyManager.Enemy = None
        self.__showHPTime : int = 0
        
        self.damage = 30

    def getName(self) :
        return '플레이어'

    def setTarget(self, enemy) :
        import GameManager 
        self.__target = enemy
        self.__showHPTime = GameManager.DelayTime.SEC * 5

    def getTarget(self) :
        return self.__target

    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.extraBox)
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (200, 200, 200), self.hitbox.extraBox2)
        super().drawHitbox(screen)

    def updateHitbox(self) :
        side_hitbox_length = 50
        top_bottom_hitbox_length = 30
        offset = 20
        depth = 20
        self.hitbox.topBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom - (offset * 2) - depth - side_hitbox_length, top_bottom_hitbox_length, depth)
        self.hitbox.bottomBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom, top_bottom_hitbox_length, depth)
        self.hitbox.leftBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2) - depth, self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.rightBox.update(self.rect.centerx + (top_bottom_hitbox_length / 2), self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.damageBox.update(self.hitbox.topBox.left, self.hitbox.topBox.bottom, top_bottom_hitbox_length, side_hitbox_length + (offset * 2))
        if self.animationController.flip.x :
            self.hitbox.extraBox.update(self.hitbox.leftBox.left - depth, self.hitbox.topBox.top, depth, depth)
            self.hitbox.extraBox2.update(self.hitbox.extraBox.left, self.hitbox.extraBox.top - depth, depth, depth)
        else :
            self.hitbox.extraBox.update(self.hitbox.rightBox.right, self.hitbox.topBox.top, depth, depth)
            self.hitbox.extraBox2.update(self.hitbox.extraBox.left, self.hitbox.extraBox.top - depth, depth, depth)

    def death(self, killer) :
        import EventManager
        event = EventManager.EntityDeathEvent(self, killer)
        event.call()

        if not event.isCancelled() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('death', True)

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        import EventManager
        import ParticleManager
        import GameManager
        event = EventManager.EntityDamageEvent(self, attacker, damage, knockBack)
        event.call()

        if self.animationController.getCurrentAnimation().name == 'parry_stance' :
            if (self.hitbox.damageBox.centerx <= event.getAttacker().rect.centerx and not self.animationController.flip.x) or (event.getAttacker().rect.centerx < self.hitbox.damageBox.centerx and self.animationController.flip.x) :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('parry', True)
                self.animationController.waitAnimation('sheath_sword', False, True, 2)
                self.animationController.waitAnimation('idle', True)
                self.parryCoolDown = 0
                event.cancel()
        
        if not event.isCancelled() :
            self.health -= event.getDamage()
            ParticleManager.TextParticle(pygame.Vector3(self.position.x, self.position.y - self.rect.height, 0), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), str(event.getAttacker().getName()) + ' 의 공격력 1 증가', (255, 0, 0), GameManager.DelayTime.SEC * 2).setWorld(self.getWorld())
            event.getAttacker().damage += 1
            knockBack = event.getKnockBack()
            if self.hitbox.damageBox.centerx <= event.getAttacker().rect.centerx :
                self.knockback(pygame.Vector2(knockBack * -1, knockBack.y))
                
            else :
                self.knockback(knockBack)

            if self.health <= 0 :
                self.death(attacker)

            else :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('hurt', True)
                self.animationController.waitAnimation('idle', True)

        super().damaged(attacker, event.getDamage(), event.getKnockBack())

    def update(self, deltaTime : float) :
        import GameManager
        import ParticleManager
        camera = GameManager.Game.getInstance().getScreenController().camera
        camera.target = pygame.Vector2(self.position.x, self.position.y) - camera.offset
        keyState = GameManager.Game.getInstance().keyState

        self.parryCoolDown = max(0, self.parryCoolDown - deltaTime)
        self.dodgeCoolDown = max(0, self.dodgeCoolDown - deltaTime)
        self.__showHPTime = max(0, self.__showHPTime - deltaTime)

        self.getWorld().playTime += deltaTime

        if self.__showHPTime <= 0 :
            self.setTarget(None)

        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        if self.getWorld().isOnline :
            allDead = True
            for living in self.getWorld().getLivings() :
                if living.health > 0 :
                    allDead = False
                    break

            if allDead and not self.getWorld().isClear :
                self.getWorld().isClear = True
        
# ===== Key 입력 처리 =====
        if keyState.j :
            if self.isGround() and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run'] :
                if self.__punchMotion == 0 and self.animationController.getCurrentAnimation().name != 'first_punch' :
                    self.animationController.clearWaiting()
                    self.animationController.playAnimation('first_punch', True)

                elif self.__punchMotion == 1 and self.animationController.getCurrentAnimation().name != 'second_punch' :
                    self.animationController.clearWaiting()
                    self.animationController.playAnimation('second_punch', True)

                self.__punchMotion = (self.__punchMotion + 1) % 2

            elif keyState.up and self.currentJumpCount > 0 and not self.isGround() and self.animationController.getCurrentAnimation().name in ['jump', 'fall'] :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('air_down_punch', True)
                self.animationController.waitAnimation('fall', True)
                self.currentJumpCount -= 1

        if not keyState.j and self.animationController.getCurrentAnimation().name in ['first_punch', 'second_punch'] and (self.animationController.isEnd() or 6 <= self.animationController.getCurrentIndex() and self.animationController.getCurrentIndex() <= 7) :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)

        if keyState.k :
            if (self.isGround() and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run']) or (self.animationController.getCurrentAnimation().name in ['first_sword', 'second_sword', 'third_sword'] and self.animationController.isEnd()) :
                if self.__swordMotion == 0 and self.animationController.getCurrentAnimation().name != 'first_sword' :
                    self.animationController.clearWaiting()
                    self.animationController.playAnimation('first_sword', True)

                elif self.__swordMotion == 1 and self.animationController.getCurrentAnimation().name != 'second_sword' :
                    self.animationController.clearWaiting()
                    self.animationController.playAnimation('second_sword', True)

                elif self.__swordMotion == 2 and self.animationController.getCurrentAnimation().name != 'third_sword' :
                    self.animationController.clearWaiting()
                    self.animationController.playAnimation('third_sword', True)
                
                self.__swordMotion = (self.__swordMotion + 1) % 3
            
            elif keyState.down and not self.isGround() and self.animationController.getCurrentAnimation().name in ['jump', 'fall'] :
                self.moveDir.y = self.jumpPower * 2
                self.animationController.clearWaiting()
                self.animationController.playAnimation('air_slam', True)


        if not keyState.k and self.animationController.getCurrentAnimation().name in ['first_sword', 'second_sword', 'third_sword'] and self.animationController.isEnd() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('sheath_sword', True)
            self.animationController.waitAnimation('idle', True)

        if self.parryCoolDown <= 0 and keyState.l and self.isGround() and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run', 'parry', 'sheath_sword'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('parry_stance', True)
            self.animationController.waitAnimation('sheath_sword')
            self.animationController.waitAnimation('idle', True)
            self.noPain = True
            keyState.l = False
            self.parryCoolDown = self.__parryCoolTime

        if keyState.left and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run', 'jump', 'fall', 'air_down_punch'] :
            self.moveDir.x = max(-1, self.moveDir.x - 0.01 * deltaTime * self.speedOfTime)

        if keyState.right and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run', 'jump', 'fall', 'air_down_punch'] :
            self.moveDir.x = min(1, self.moveDir.x + 0.01 * deltaTime * self.speedOfTime)

        if keyState.up and self.animationController.getCurrentAnimation().name == 'dangle' :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('wall_climb', True)
            self.animationController.waitAnimation('idle', True)

        if keyState.down and self.animationController.getCurrentAnimation().name in ['idle', 'run_start', 'run'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('crouch', True)

        if not keyState.down and self.animationController.getCurrentAnimation().name == 'crouch' and self.animationController.isEnd() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('stand_up', True)
            self.animationController.waitAnimation('idle', True)

        if self.dodgeCoolDown <= 0 and keyState.lshift and self.animationController.getCurrentAnimation().name == 'run' :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('dodge', True)
            keyState.lshift = False
            self.dodgeCoolDown = self.__dodgeCoolTime
            if self.animationController.flip.x :
                self.moveDir.x = -3
                
            else :
                self.moveDir.x = 3

        if keyState.space and not self.moveLock.y and self.currentJumpCount > 0 and self.animationController.getCurrentAnimation().name not in ['dodge', 'dodge_end', 'landing', 'air_slam', 'air_slam_landing', 'air_down_punch', 'parry_stance', 'parry', 'hurt', 'death'] :
            particle = ParticleManager.JumpParticle(self, pygame.Vector3(self.position), 1)
            particle.playParticle()
            self.jump()
            self.currentJumpCount -= 1
            keyState.space = False

# ===== Animation 처리 =====
        
        self.moveLock.update(False, False)
        if self.animationController.getCurrentAnimation().name in ['landing', 'crouch', 'stand_up', 'air_slam', 'air_slam_landing'] :
            self.moveLock.x = True

        if self.animationController.getCurrentAnimation().name in ['wall_grap', 'dangle', 'wall_climb', 'first_punch', 'second_punch', 'first_sword', 'second_sword', 'third_sword'] :
            self.moveLock.update(True, True)
            self.moveDir.update(0, 0)

        self.noPain = False
        if self.animationController.getCurrentAnimation().name in ['landing', 'dodge', 'dodge_end', 'hurt', 'death'] :
            self.noPain = True

        if self.moveDir.y < 0 : # 음수는 위 양수는 아래
            self.lastHeight = self.position.y

        self.hitbox.clearExtra()
        if self.animationController.getCurrentAnimation().name in ['jump', 'fall', 'air_down_punch'] :
            isTop = True
            for block in self.getWorld().getBlocks() :
                if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox, block.rect) :
                    self.hitbox.extra = block
                
                if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox2, block.rect) :
                    isTop = False
            
            if isTop and self.hitbox.extra != None : 
                self.animationController.clearWaiting()
                self.animationController.playAnimation('wall_grap', True)
                self.animationController.waitAnimation('dangle', True)
                self.moveLock.update(True, True)
                if self.animationController.flip.x :
                    self.position.x = self.hitbox.extra.position.x + self.hitbox.extra.rect.width - 84
                    self.position.y = self.hitbox.extra.position.y - self.hitbox.extra.rect.height + 92

                else :
                    self.position.x = self.hitbox.extra.position.x - 116
                    self.position.y = self.hitbox.extra.position.y - self.hitbox.extra.rect.height + 92

        if not keyState.isPressedXAxis() and self.isGround() and self.animationController.getCurrentAnimation().name not in ['idle', 'jump', 'fall', 'landing', 'wall_grap', 'dangle', 'wall_climb', 'dodge', 'dodge_end', 'crouch', 'stand_up', 'first_punch', 'second_punch', 'first_sword', 'second_sword', 'third_sword', 'sheath_sword', 'air_slam', 'air_slam_landing', 'parry_stance', 'parry', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)

        elif not self.moveLock.x and keyState.isPressedXAxis() and self.isGround() and self.animationController.getCurrentAnimation().name not in ['run_start', 'run', 'fall', 'landing', 'wall_grap', 'dangle', 'wall_climb', 'dodge', 'dodge_end', 'first_punch', 'second_punch', 'first_sword', 'second_sword', 'third_sword', 'sheath_sword', 'air_slam', 'air_slam_landing', 'parry_stance', 'parry', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('run_start', True)
            self.animationController.waitAnimation('run', True, True, self.multipleSpeed)

        if not self.moveLock.y and int(self.moveDir.y) < 0 and self.animationController.getCurrentAnimation().name in ['idle', 'jump', 'fall', 'run_start', 'run'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('jump', True)

        elif not self.moveLock.y and int(self.moveDir.y) > 0 and not self.isGround() and self.animationController.getCurrentAnimation().name not in ['air_slam', 'air_down_punch'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('fall', True, True)

        elif self.animationController.getCurrentAnimation().name in ['jump', 'fall', 'air_down_punch'] and self.isGround() :
            self.animationController.clearWaiting()
            if self.position.y - self.lastHeight >= 250 : #떨어진 높이
                particle = ParticleManager.LandingParticle(self, pygame.Vector3(self.position), 1)
                particle.playParticle()
                self.animationController.playAnimation('landing', True)
                self.animationController.waitAnimation('idle', True)
                
            else :
                self.animationController.playAnimation('idle', True, True)

        if self.animationController.getCurrentAnimation().name == 'air_slam' and self.isGround() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('air_slam_landing', True)
            self.animationController.waitAnimation('idle', True)

        if self.animationController.getCurrentAnimation().name == 'dodge' and abs(self.moveDir.x) <= 1 :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('dodge_end', True)
            self.animationController.waitAnimation('idle', True)

        if self.animationController.getCurrentAnimation().name in ['idle', 'run'] :
            self.currentJumpCount = self.maxJumpCount

        if not self.moveLock.x and self.moveDir.x != 0 and self.animationController.getCurrentAnimation().name in ['run_start', 'run', 'jump', 'fall', 'air_down_punch']:
            self.animationController.flip.x = self.moveDir.x < 0

        super().update(deltaTime)