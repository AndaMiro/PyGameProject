import pygame
import EntityManager

class Enemy(EntityManager.Living) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)

    def getName(self) :
        return ''

class SmallMonster(Enemy) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)
        import AnimationManager
        import GameManager
        self.animationController.addAnimation(AnimationManager.SmallMonsterIdle())
        self.animationController.addAnimation(AnimationManager.SmallMonsterRun())
        self.animationController.addAnimation(AnimationManager.SmallMonsterAttack())
        self.animationController.addAnimation(AnimationManager.SmallMonsterHurt())
        self.animationController.addAnimation(AnimationManager.SmallMonsterDeath())

        self.__turnCoolDown : int = 0
        self.__turnCoolTime : int = GameManager.DelayTime.SEC * 3
        self.__attackCoolDown : int = 0
        self.__attackCoolTime : int = 0

    def getName(self) :
        return '불 마법사'

    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.extraBox)
        super().drawHitbox(screen)

    def updateHitbox(self) :
        side_hitbox_length = 50
        top_bottom_hitbox_length = 50
        offset = 20
        depth = 5
        self.hitbox.topBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom - (offset * 2) - depth - side_hitbox_length, top_bottom_hitbox_length, depth)
        self.hitbox.bottomBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom, top_bottom_hitbox_length, depth)
        self.hitbox.leftBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2) - depth, self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.rightBox.update(self.rect.centerx + (top_bottom_hitbox_length / 2), self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.damageBox.update(self.hitbox.topBox.left, self.hitbox.topBox.bottom, top_bottom_hitbox_length, side_hitbox_length + (offset * 2))
        self.hitbox.scanBox.update(self.rect.centerx - 500, self.hitbox.topBox.bottom - 100, 1000, side_hitbox_length + 100 + (offset * 2))
        if self.animationController.flip.x :
            self.hitbox.extraBox.update(self.hitbox.leftBox.left - depth * 5, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)
       
        else :
            self.hitbox.extraBox.update(self.hitbox.rightBox.right, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

    def death(self, killer) :
        import EventManager
        event = EventManager.EntityDeathEvent(self, killer)
        event.call()

        if not event.isCancelled() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('death', True)

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        import EventManager
        event = EventManager.EntityDamageEvent(self, attacker, damage, knockBack)
        event.call()

        if not event.isCancelled() :
            self.health -= event.getDamage()
            if self.health <= 0 :
                self.death(attacker)

            else :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('hurt', True)
                self.animationController.waitAnimation('idle', True)
                knockBack = event.getKnockBack()
                if self.hitbox.damageBox.centerx <= event.getAttacker().rect.centerx :
                    self.knockback(pygame.Vector2(knockBack.x * -1, knockBack.y))
            
                else :
                    self.knockback(knockBack)

        super().damaged(attacker, event.getDamage(), event.getKnockBack())
        
    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        self.__attackCoolDown = max(0, self.__attackCoolDown - deltaTime)

        self.hitbox.clearExtra()
        for block in self.getWorld().getBlocks() :
            if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox, block.rect) :
                self.hitbox.extra = block

        if self.hitbox.left != None or self.hitbox.right != None or self.hitbox.extra == None :
            self.__turnCoolDown -= deltaTime

        if self.__turnCoolDown <= 0 :
            self.animationController.flip.x = not self.animationController.flip.x
            self.__turnCoolDown = self.__turnCoolTime

        self.noPain = False
        if self.animationController.getCurrentAnimation().name in ['hurt', 'death'] :
            self.noPain = True

        player = GameManager.Game.getInstance().getPlayer()
        if self.animationController.getCurrentAnimation().name not in ['attack', 'hurt', 'death'] and pygame.Rect.colliderect(self.hitbox.scanBox, player.hitbox.damageBox) :
            if self.hitbox.damageBox.centerx <= player.hitbox.damageBox.centerx :
                self.animationController.flip.x = False
            else :
                self.animationController.flip.x = True

        if self.animationController.getCurrentAnimation().name in ['idle', 'run'] and pygame.Rect.colliderect(self.rect, player.hitbox.damageBox) :
            if self.__attackCoolDown <= 0 :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('attack', True)
                self.animationController.waitAnimation('idle', True)
                self.__attackCoolDown = self.__attackCoolTime

        if self.animationController.getCurrentAnimation().name not in ['attack', 'hurt', 'death'] and self.hitbox.extra != None :
            self.moveDir.x = 0
            if self.animationController.flip.x :
                self.moveDir.x = -1 

            else :
                self.moveDir.x = 1

        self.moveLock.update(False, False)
        if self.animationController.getCurrentAnimation().name in ['attack', 'death'] :
            self.moveLock.x = True

        if self.moveDir.x == 0 and self.animationController.getCurrentAnimation().name not in ['idle', 'attack', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)
        
        elif not self.moveLock.x and self.moveDir.x != 0 and self.animationController.getCurrentAnimation().name not in ['run', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('run', True, True)

        super().update(deltaTime)

class GunMonster(Enemy) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)
        import AnimationManager
        import GameManager
        self.animationController.addAnimation(AnimationManager.GunMonsterIdle())
        self.animationController.addAnimation(AnimationManager.GunMonsterWakeUp())
        self.animationController.addAnimation(AnimationManager.GunMonsterSleep())
        self.animationController.addAnimation(AnimationManager.GunMonsterRun())
        self.animationController.addAnimation(AnimationManager.GunMonsterCharge())
        self.animationController.addAnimation(AnimationManager.GunMonsterAttack())
        self.animationController.addAnimation(AnimationManager.GunMonsterHurt())
        self.animationController.addAnimation(AnimationManager.GunMonsterDeath())

        self.__attackCoolDown : int = 0
        self.__attackCoolTime : int = 0

    def getName(self) :
        return '사냥꾼' 

    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.extraBox)
        super().drawHitbox(screen)

    def updateHitbox(self) :
        side_hitbox_length = 50
        top_bottom_hitbox_length = 50
        offset = 20
        depth = 5
        self.hitbox.topBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom - (offset * 2) - depth - side_hitbox_length, top_bottom_hitbox_length, depth)
        self.hitbox.bottomBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom, top_bottom_hitbox_length, depth)
        self.hitbox.leftBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2) - depth, self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.rightBox.update(self.rect.centerx + (top_bottom_hitbox_length / 2), self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.damageBox.update(self.hitbox.topBox.left, self.hitbox.topBox.bottom, top_bottom_hitbox_length, side_hitbox_length + (offset * 2))
        self.hitbox.scanBox.update(self.rect.centerx - 500, self.hitbox.topBox.bottom - 100, 1000, side_hitbox_length + 100 + (offset * 2))
        if self.animationController.flip.x :
            self.hitbox.extraBox.update(self.hitbox.leftBox.left - depth * 5, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

        else :
            self.hitbox.extraBox.update(self.hitbox.rightBox.right, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

    def death(self, killer) :
        import EventManager
        event = EventManager.EntityDeathEvent(self, killer)
        event.call()

        if not event.isCancelled() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('death', True)

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        import EventManager
        event = EventManager.EntityDamageEvent(self, attacker, damage, knockBack)
        event.call()

        if not event.isCancelled() :
            self.health -= event.getDamage()
            if self.health <= 0 :
                self.death(attacker)

            else :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('hurt', True)
                self.animationController.waitAnimation('run', True)
                knockBack = event.getKnockBack()
                if self.hitbox.damageBox.centerx <= event.getAttacker().rect.centerx :
                    self.knockback(pygame.Vector2(knockBack.x * -1, knockBack.y))
                
                else :
                    self.knockback(knockBack)

        super().damaged(attacker, event.getDamage(), event.getKnockBack())
        
    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        self.__attackCoolDown = max(0, self.__attackCoolDown - deltaTime)

        self.hitbox.clearExtra()
        for block in self.getWorld().getBlocks() :
            if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox, block.rect) :
                self.hitbox.extra = block

        self.noPain = False
        if self.animationController.getCurrentAnimation().name in ['hurt', 'death'] :
            self.noPain = True

        player = GameManager.Game.getInstance().getPlayer()
        if pygame.Rect.colliderect(self.hitbox.scanBox, player.hitbox.damageBox) :
            if self.animationController.getCurrentAnimation().name in ['idle', 'run', 'charge'] :
                if self.hitbox.damageBox.centerx <= player.hitbox.damageBox.centerx :
                    self.animationController.flip.x = False

                else :
                    self.animationController.flip.x = True

            if self.animationController.getCurrentAnimation().name == 'idle' and self.hitbox.extra != None :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('wake_up', True)
                self.animationController.waitAnimation('run', True)
            
            elif self.animationController.getCurrentAnimation().name in ['run'] :
                self.moveDir.x = 0
                if self.hitbox.extra != None :
                    if self.animationController.flip.x :
                        self.moveDir.x = -1

                    else :
                        self.moveDir.x = 1

        if self.animationController.getCurrentAnimation().name in ['run'] and pygame.Rect.colliderect(self.rect, player.hitbox.damageBox) :
            if abs(player.hitbox.damageBox.centerx - self.rect.centerx) <= 50 :
                self.moveDir.x = 0

            if self.__attackCoolDown <= 0 :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('charge', True)
                self.animationController.waitAnimation('attack')
                self.animationController.waitAnimation('run')
                self.__attackCoolDown = self.__attackCoolTime

        if self.moveDir.x == 0 and self.animationController.getCurrentAnimation().name == 'run' :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('sleep', True)
            self.animationController.waitAnimation('idle', True)

        self.moveLock.update(False, False)
        if self.animationController.getCurrentAnimation().name in ['charge', 'attack', 'death'] :
            self.moveLock.x = True

        if self.moveDir.x == 0 and self.animationController.getCurrentAnimation().name not in ['idle', 'wake_up', 'sleep', 'charge', 'attack', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)
        
        elif not self.moveLock.x and self.moveDir.x != 0 and self.animationController.getCurrentAnimation().name not in ['run', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('run', True, True)

        super().update(deltaTime)

class SwordMonster(Enemy) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)
        import AnimationManager
        import GameManager
        self.animationController.addAnimation(AnimationManager.SwordMonsterIdle())
        self.animationController.addAnimation(AnimationManager.SwordMonsterRun())
        self.animationController.addAnimation(AnimationManager.SwordMonsterAttack())
        self.animationController.addAnimation(AnimationManager.SwordMonsterHurt())
        self.animationController.addAnimation(AnimationManager.SwordMonsterDeath())

        self.__turnCoolDown : int = 0
        self.__turnCoolTime : int = GameManager.DelayTime.SEC * 3
        self.__attackCoolDown : int = 0
        self.__attackCoolTime : int = 0

    def getName(self) :
        return '검사'

    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.extraBox)
        super().drawHitbox(screen)

    def updateHitbox(self) :
        side_hitbox_length = 50
        top_bottom_hitbox_length = 50
        offset = 20
        depth = 5
        self.hitbox.topBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom - (offset * 2) - depth - side_hitbox_length, top_bottom_hitbox_length, depth)
        self.hitbox.bottomBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom, top_bottom_hitbox_length, depth)
        self.hitbox.leftBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2) - depth, self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.rightBox.update(self.rect.centerx + (top_bottom_hitbox_length / 2), self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.damageBox.update(self.hitbox.topBox.left, self.hitbox.topBox.bottom, top_bottom_hitbox_length, side_hitbox_length + (offset * 2))
        self.hitbox.scanBox.update(self.rect.centerx - 500, self.hitbox.topBox.bottom - 100, 1000, side_hitbox_length + 100 + (offset * 2))
        if self.animationController.flip.x :
            self.hitbox.extraBox.update(self.hitbox.leftBox.left - depth * 5, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

        else :
            self.hitbox.extraBox.update(self.hitbox.rightBox.right, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

    def death(self, killer) :
        import EventManager
        event = EventManager.EntityDeathEvent(self, killer)
        event.call()

        if not event.isCancelled() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('death', True)

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        import EventManager
        event = EventManager.EntityDamageEvent(self, attacker, damage, knockBack)
        event.call()

        if not event.isCancelled() :
            self.health -= event.getDamage()
            if self.health <= 0 :
                self.death(attacker)

            else :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('hurt', True)
                self.animationController.waitAnimation('idle', True)
                knockBack = event.getKnockBack()
                if self.hitbox.damageBox.centerx <= event.getAttacker().rect.centerx :
                    self.knockback(pygame.Vector2(knockBack.x * -1, knockBack.y))
            
                else :
                    self.knockback(knockBack)

        super().damaged(attacker, event.getDamage(), event.getKnockBack())
        
    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        self.__attackCoolDown = max(0, self.__attackCoolDown - deltaTime)

        self.hitbox.clearExtra()
        for block in self.getWorld().getBlocks() :
            if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox, block.rect) :
                self.hitbox.extra = block

        if self.hitbox.left != None or self.hitbox.right != None or self.hitbox.extra == None :
            self.__turnCoolDown -= deltaTime

        if self.__turnCoolDown <= 0 :
            self.animationController.flip.x = not self.animationController.flip.x
            self.__turnCoolDown = self.__turnCoolTime

        self.noPain = False
        if self.animationController.getCurrentAnimation().name in ['hurt', 'death'] :
            self.noPain = True

        player = GameManager.Game.getInstance().getPlayer()
        if self.animationController.getCurrentAnimation().name not in ['attack', 'hurt', 'death'] and pygame.Rect.colliderect(self.hitbox.scanBox, player.hitbox.damageBox) :
            if self.hitbox.damageBox.centerx <= player.hitbox.damageBox.centerx :
                self.animationController.flip.x = False
            else :
                self.animationController.flip.x = True

        if self.animationController.getCurrentAnimation().name in ['idle', 'run'] and pygame.Rect.colliderect(self.rect, player.hitbox.damageBox) :
            if abs(player.hitbox.damageBox.centerx - self.rect.centerx) <= 50 :
                self.moveDir.x = 0

            if self.__attackCoolDown <= 0 :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('attack', True)
                self.animationController.waitAnimation('idle', True)
                self.__attackCoolDown = self.__attackCoolTime

        if self.animationController.getCurrentAnimation().name not in ['attack', 'hurt', 'death'] and self.hitbox.extra != None :
            self.moveDir.x = 0
            if self.animationController.flip.x :
                self.moveDir.x = -1 

            else :
                self.moveDir.x = 1

        self.moveLock.update(False, False)
        if self.animationController.getCurrentAnimation().name in ['attack', 'death'] :
            self.moveLock.x = True

        if self.moveDir.x == 0 and self.animationController.getCurrentAnimation().name not in ['idle', 'attack', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)
        
        elif not self.moveLock.x and self.moveDir.x != 0 and self.animationController.getCurrentAnimation().name not in ['run', 'hurt', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('run', True, True)

        super().update(deltaTime)

class RobotBoss(Enemy) :
    def __init__(self, position : pygame.Vector3, defaultSpeed : float, jumpPower : float, health : int, airResistance : float, gravity : float) :
        super().__init__(position, defaultSpeed, jumpPower, health, airResistance, gravity)
        import AnimationManager
        import GameManager
        self.animationController.addAnimation(AnimationManager.RobotBossIdle())
        self.animationController.addAnimation(AnimationManager.RobotBossRun())
        self.animationController.addAnimation(AnimationManager.RobotBossShield())
        self.animationController.addAnimation(AnimationManager.RobotBossAttack())
        self.animationController.addAnimation(AnimationManager.RobotBossDeath())

        self.__turnCoolDown : int = 0
        self.__turnCoolTime : int = GameManager.DelayTime.SEC * 3
        self.__attackCoolDown : int = 0
        self.__attackCoolTime : int = GameManager.DelayTime.SEC * 5

    def getName(self) :
        return '로봇 보스'

    def drawHitbox(self, screen : pygame.Surface) :
        import GameManager
        pygame.draw.rect(GameManager.Game.getInstance().getScreenController().screen, (255, 255, 255), self.hitbox.extraBox)
        super().drawHitbox(screen)

    def updateHitbox(self) :
        side_hitbox_length = 200
        top_bottom_hitbox_length = 200
        offset = 40
        depth = 20
        self.hitbox.topBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom - (offset * 2) - depth - side_hitbox_length, top_bottom_hitbox_length, depth)
        self.hitbox.bottomBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2), self.rect.bottom, top_bottom_hitbox_length, depth)
        self.hitbox.leftBox.update(self.rect.centerx - (top_bottom_hitbox_length / 2) - depth, self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.rightBox.update(self.rect.centerx + (top_bottom_hitbox_length / 2), self.rect.bottom - offset - side_hitbox_length, depth, side_hitbox_length)
        self.hitbox.damageBox.update(self.hitbox.topBox.left, self.hitbox.topBox.bottom, top_bottom_hitbox_length, side_hitbox_length + (offset * 2))
        self.hitbox.scanBox.update(self.rect.centerx - 500, self.hitbox.topBox.bottom - 100, 1000, side_hitbox_length + 100 + (offset * 2))
        if self.animationController.flip.x :
            self.hitbox.extraBox.update(self.hitbox.leftBox.left - depth * 5, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

        else :
            self.hitbox.extraBox.update(self.hitbox.rightBox.right, self.hitbox.bottomBox.bottom, depth * 5, depth * 5)

    def death(self, killer) :
        import EventManager
        event = EventManager.EntityDeathEvent(self, killer)
        event.call()

        if not event.isCancelled() :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('death', True)

    def damaged(self, attacker, damage : float, knockBack : pygame.Vector2) :
        import EventManager
        import GameManager
        import ParticleManager
        event = EventManager.EntityDamageEvent(self, attacker, damage, knockBack)
        event.call()
        beforeHealth = self.health

        if not event.isCancelled() :
            self.health -= event.getDamage()
            if self.health <= 0 :
                self.death(attacker)

            if beforeHealth > self.maxHealth / 2 and self.health <= self.maxHealth / 2 :
                ParticleManager.TextParticle(pygame.Vector3(self.position.x + 100, self.position.y - (self.rect.height / 2) - 50, 0), pygame.font.Font('Fonts\\HBIOS-SYS.ttf', 30), self.getName() + '의 공격력이 50% 상승합니다.', (114, 187, 237), GameManager.DelayTime.SEC * 10).setWorld(self.getWorld())
                self.damage += int(self.damage / 2)
                self.animationController.clearWaiting()
                self.animationController.playAnimation('shield', True)
                self.animationController.waitAnimation('idle', True)

        super().damaged(attacker, event.getDamage(), event.getKnockBack())

    def update(self, deltaTime : float) :
        import GameManager
        if self.animationController.getCurrentAnimation() == None :
            self.animationController.waitAnimation('idle', True)

        self.__attackCoolDown = max(0, self.__attackCoolDown - deltaTime)

        self.hitbox.clearExtra()
        for block in self.getWorld().getBlocks() :
            if block.isCollision and pygame.Rect.colliderect(self.hitbox.extraBox, block.rect) :
                self.hitbox.extra = block

        if self.hitbox.left != None or self.hitbox.right != None or self.hitbox.extra == None :
            self.__turnCoolDown -= deltaTime

        if self.__turnCoolDown <= 0 :
            self.animationController.flip.x = not self.animationController.flip.x
            self.__turnCoolDown = self.__turnCoolTime

        self.noPain = False
        if self.animationController.getCurrentAnimation().name in ['shield', 'death'] :
            self.noPain = True

        player = GameManager.Game.getInstance().getPlayer()
        if self.animationController.getCurrentAnimation().name not in ['shield', 'attack', 'death'] and pygame.Rect.colliderect(self.hitbox.scanBox, player.hitbox.damageBox) :
            if self.hitbox.damageBox.centerx <= player.hitbox.damageBox.centerx :
                self.animationController.flip.x = False
            else :
                self.animationController.flip.x = True

        if self.animationController.getCurrentAnimation().name not in ['shield', 'attack', 'death'] and self.hitbox.extra != None :
            self.moveDir.x = 0
            if self.animationController.flip.x :
                self.moveDir.x = -1 

            else :
                self.moveDir.x = 1

        if self.animationController.getCurrentAnimation().name in ['idle', 'run'] and pygame.Rect.colliderect(self.rect, player.hitbox.damageBox) :
            if abs(player.hitbox.damageBox.centerx - self.rect.centerx) <= 250 :
                self.moveDir.x = 0

            if self.__attackCoolDown <= 0 :
                self.animationController.clearWaiting()
                self.animationController.playAnimation('attack', True)
                self.animationController.waitAnimation('idle', True)
                self.__attackCoolDown = self.__attackCoolTime

        self.moveLock.update(False, False)
        if self.animationController.getCurrentAnimation().name in ['shield', 'attack', 'death'] :
            self.moveLock.x = True

        if self.moveDir.x == 0 and self.animationController.getCurrentAnimation().name not in ['idle', 'shield', 'attack', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('idle', True, True)
        
        elif not self.moveLock.x and self.moveDir.x != 0 and self.animationController.getCurrentAnimation().name not in ['run', 'shield', 'death'] :
            self.animationController.clearWaiting()
            self.animationController.playAnimation('run', True, True)

        super().update(deltaTime)