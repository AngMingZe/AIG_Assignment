import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Archer_EZ(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None
        self.targetPos = (230,100)

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = ArcherStateSeeking_EZ(self)
        attacking_state = ArcherStateAttacking_EZ(self)
        ko_state = ArcherStateKO_EZ(self)
        dodging_state = ArcherStateDodging_EZ(self)
        roaming_state = ArcherStateRoaming_EZ(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(roaming_state)
        self.brain.add_state(dodging_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        if self.can_level_up():
            choice = 2
            self.level_up(level_up_stats[choice])   


class ArcherStateSeeking_EZ(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        self.archer.path_graph = self.archer.world.paths[1]


    def do_actions(self):

        if self.archer.current_hp != self.archer.max_hp:
            self.archer.heal()

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"
        
        if (self.archer.position - self.archer.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position


class ArcherStateAttacking_EZ(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer

    def do_actions(self):

        opponent_distance = (self.archer.position - self.archer.target.position).length()

        # opponent within range
        if opponent_distance <= self.archer.min_target_distance:
            self.archer.velocity = Vector2(0, 0)
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)

        else:
            self.archer.velocity = self.archer.target.position - self.archer.position
            if self.archer.velocity.length() > 0:
                self.archer.velocity.normalize_ip();
                self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        if self.archer.current_ranged_cooldown > 0:
            return "dodging"
        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            towerCount = 0
            for entity in self.archer.world.entities.values():
                if entity.name == "tower" and entity.team_id != self.archer.team_id and entity.team_id != 2:
                    towerCount += 1
            if (towerCount == 2):
                self.archer.path_graph = self.archer.world.paths[1]
                return "seeking"
            else:
                self.targetPos = (230, 100)
                return "roaming"
         

        return None

    def entry_actions(self):

        return None


class ArcherStateKO_EZ(State):

    def __init__(self, archer):

        State.__init__(self, "ko")
        self.archer = archer

    def do_actions(self):

        return None


    def check_conditions(self):

        if self.archer.current_respawn_time <= 0:
            self.archer.current_respawn_time = self.archer.respawn_time
            self.archer.ko = False
            towerCount = 0
            for entity in self.archer.world.entities.values():
                if entity.name == "tower" and entity.team_id != self.archer.team_id and entity.team_id != 2:
                    towerCount += 1
            if (towerCount == 2):
                self.archer.path_graph = self.archer.world.paths[1]
                return "seeking"
            else:
                self.targetPos = (230, 100)
                return "roaming"

        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None

class ArcherStateRoaming_EZ(State):

    def __init__(self, archer):

        State.__init__(self, "roaming")
        self.archer = archer
    
    def do_actions(self):

        if self.archer.current_hp != self.archer.max_hp:
            self.archer.heal()

        #self.archer.base.spawn_position
        if self.archer.team_id == 0:
            if (self.archer.position - self.archer.targetPos).length() <= 3 and self.archer.targetPos == (230,100):
                self.archer.targetPos = (75, 200)
            if (self.archer.position - self.archer.targetPos).length() <= 3 and self.archer.targetPos == (75, 200):
                self.archer.targetPos = (230, 100)
        else:
            if (self.archer.position - self.archer.targetPos).length() <= 3 and self.archer.targetPos == (794,668):
                self.archer.targetPos = (949, 568)
            if (self.archer.position - self.archer.targetPos).length() <= 3 and self.archer.targetPos == (814, 568):
                self.archer.targetPos = (794, 924)

        distance = (self.archer.position - self.archer.targetPos).length()

        self.archer.velocity = self.archer.targetPos - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"

    
    def entry_actions(self):

        self.archer.target = None

class ArcherStateDodging_EZ(State):

    def __init__(self, archer):

        State.__init__(self, "dodging")
        self.archer = archer

    def do_actions(self):

        distance = (self.archer.target.position - self.archer.position).length()
        if distance < 75:
            self.archer.velocity = + self.archer.position - self.archer.target.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed
    
    def check_conditions(self):
        if self.archer.current_ranged_cooldown <= 0:
            return "attacking"
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko or self.archer.velocity==0:
            self.archer.target = None
            return "seeking"

    def entry_actions(self):

        return None