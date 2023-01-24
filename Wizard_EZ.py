import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Wizard_EZ(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "ezWizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None
        self.targetPos = (147,147)

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        roaming_state = WizardStateRoaming_EZ(self)
        attacking_state = WizardStateAttacking_EZ(self)
        ko_state = WizardStateKO_EZ(self)

        self.brain.add_state(roaming_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("roaming")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range", "healing", "healing cooldown"]
        if self.can_level_up():
            choice = 3
            self.level_up(level_up_stats[choice])


class WizardStateRoaming_EZ(State):

    def __init__(self, wizard):

        State.__init__(self, "roaming")
        self.wizard = wizard
    
    def do_actions(self):

        if self.wizard.current_hp != self.wizard.max_hp:
            self.wizard.heal()

        towerCount = 0
        for entity in self.wizard.world.entities.values():
            if entity.name == "tower" and entity.team_id != self.wizard.team_id and entity.team_id != 2:
                towerCount += 1
        if (towerCount == 2):
            if self.wizard.team_id == 0:
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (147,147):
                    self.wizard.targetPos = (210, 50)
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (210, 50):
                    self.wizard.targetPos = (147, 147)
            else:
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (877,621):
                    self.wizard.targetPos = (814, 718)
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (814, 718):
                    self.wizard.targetPos = (877, 621)
        else:
            if self.wizard.team_id == 0:
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (230,100):
                    self.wizard.targetPos = (75, 200)
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (75, 200):
                    self.wizard.targetPos = (230, 100)
            else:
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (794,668):
                    self.wizard.targetPos = (949, 568)
                if (self.wizard.position - self.wizard.targetPos).length() <= 3 and self.wizard.targetPos == (814, 568):
                    self.wizard.targetPos = (794, 924)

        distance = (self.wizard.position - self.wizard.targetPos).length()

        self.wizard.velocity = self.wizard.targetPos - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if opponent_distance <= self.wizard.min_target_distance:
                    self.wizard.target = nearest_opponent
                    return "attacking"

    
    def entry_actions(self):

        self.wizard.target = None

class WizardStateAttacking_EZ(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard

    def do_actions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        # opponent within range
        if opponent_distance <= self.wizard.min_target_distance:
            self.wizard.velocity = Vector2(0, 0)
            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)

        else:
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed
            


    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            return "roaming"
            
        return None

    def entry_actions(self):

        return None


class WizardStateKO_EZ(State):

    def __init__(self, wizard):

        State.__init__(self, "ko")
        self.wizard = wizard

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.wizard.current_respawn_time <= 0:
            self.wizard.current_respawn_time = self.wizard.respawn_time
            self.wizard.ko = False
            towerCount = 0
            for entity in self.wizard.world.entities.values():
                if entity.name == "tower" and entity.team_id != self.wizard.team_id and entity.team_id != 2:
                    towerCount += 1
            if (towerCount == 2):
                self.targetPos = (147, 147)
            else:
                self.targetPos = (230, 100)
            return "roaming"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None

        list = []

