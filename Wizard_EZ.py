import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Wizard_EZ(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        #seeking_state = WizardStateSeeking_EZ(self)
        waiting_state = WizardStateWaiting_EZ(self)
        attacking_state = WizardStateAttacking_EZ(self)
        ko_state = WizardStateKO_EZ(self)
        # healing_state = WizardStateHealing_EZ(self)

        #self.brain.add_state(seeking_state)
        self.brain.add_state(waiting_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        # self.brain.add_state(healing_state)

        self.brain.set_state("waiting")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range", "healing", "healing cooldown"]
        if self.can_level_up():
            choice = 3
            self.level_up(level_up_stats[choice])

        #Healing implementation
        # nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        # if nearest_opponent is not None:
        #     opponent_distance = (self.wizard.position - nearest_opponent.position).length()
        #     if self.current_hp < 75 and opponent_distance <= self.wizard.min_target_distance:
        #         self.heal() 


class WizardStateWaiting_EZ(State):

    def __init__(self, wizard):

        State.__init__(self, "waiting")
        self.wizard = wizard
    
    def do_actions(self):

        self.wizard.heal()
        position = (275,143)
        distance = (self.wizard.position - position).length()

        # opponent within range
        if distance <= 3:
            self.wizard.velocity = Vector2(0, 0)

        else:
            self.wizard.velocity = position - self.wizard.position
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
            return "waiting"
            
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
            return "waiting"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.target = None

        return None