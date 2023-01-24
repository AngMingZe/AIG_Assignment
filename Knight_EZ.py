#THIS IS THE DRAFT/COMPLETE VERSION

import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Knight_EZ(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None
        self.targetPos = (230,100)

        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.

        seeking_state = KnightStateSeeking_EZ(self)
        attacking_state = KnightStateAttacking_EZ(self)
        ko_state = KnightStateKO_EZ(self)
        roaming_state = KnightStateRoaming_EZ(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(roaming_state)

        self.brain.set_state("seeking")
        

    def render(self, surface):
        Character.render(self, surface)


    def process(self, time_passed):
        Character.process(self, time_passed)
        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown","healing cooldown","healing"]

        if self.can_level_up():
            choice = 2
            self.level_up(level_up_stats[choice]) 
        
        #Healing implementation
        # if(self.current_hp < 100):
        #     self.heal()


class KnightStateSeeking_EZ(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight
        self.knight.path_graph = self.knight.world.paths[1] #Knight always goes bot, 1 is bot lane


    def do_actions(self):

        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed

        if self.knight.current_hp != self.knight.max_hp:
            self.knight.heal()


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
        if nearest_opponent is not None:
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                    self.knight.target = nearest_opponent
                    return "attacking"
        
        if (self.knight.position - self.knight.move_target.position).length() < 8:
            # continue on path
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None


    def entry_actions(self):
        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)
        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])

        self.path_length = len(self.path)
        if (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position
        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


class KnightStateAttacking_EZ(State):
    def __init__(self, knight):

        State.__init__(self, "attacking")
        self.knight = knight
    def do_actions(self):
        # colliding with target
        if pygame.sprite.collide_rect(self.knight, self.knight.target):
            self.knight.velocity = Vector2(0, 0)
            self.knight.melee_attack(self.knight.target)

        else:
            self.knight.velocity = self.knight.target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed

        wizard = self.knight.world.get_entity("wizard")
        distance = (self.knight.position - wizard.position).length()
        if distance < self.knight.min_target_distance:
            self.knight.target = wizard

    def check_conditions(self):
        # target is gone
        if self.knight.world.get(self.knight.target.id) is None or self.knight.target.ko:
            self.knight.target = None
            towerCount = 0
            for entity in self.knight.world.entities.values():
                if entity.name == "tower" and entity.team_id != self.knight.team_id and entity.team_id != 2:
                    towerCount += 1
            if (towerCount == 2):
                self.knight.path_graph = self.knight.world.paths[1]
                return "seeking"
            else:
                self.targetPos = (230, 100)
                return "roaming"
         
        return None

    def entry_actions(self):
        return None

class KnightStateKO_EZ(State):
    def __init__(self, knight):
        State.__init__(self, "ko")
        self.knight = knight

    def do_actions(self):
        return None

    def check_conditions(self):

        if self.knight.current_respawn_time <= 0:
            self.knight.current_respawn_time = self.knight.respawn_time
            self.knight.ko = False
            towerCount = 0
            for entity in self.knight.world.entities.values():
                if entity.name == "tower" and entity.team_id != self.knight.team_id and entity.team_id != 2:
                    towerCount += 1
            if (towerCount == 2):
                self.knight.path_graph = self.knight.world.paths[1]
                return "seeking"
            else:
                self.targetPos = (230, 100)
                return "roaming"

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None

class KnightStateRoaming_EZ(State):

    def __init__(self, knight):

        State.__init__(self, "roaming")
        self.knight = knight
    
    def do_actions(self):
        if self.knight.current_hp != self.knight.max_hp:
            self.knight.heal()
        if self.knight.team_id == 0:
            if (self.knight.position - self.knight.targetPos).length() <= 3 and self.knight.targetPos == (230,100):
                self.knight.targetPos = (75, 200)
            if (self.knight.position - self.knight.targetPos).length() <= 3 and self.knight.targetPos == (75, 200):
                self.knight.targetPos = (230, 100)
        else:
            if (self.knight.position - self.knight.targetPos).length() <= 3 and self.knight.targetPos == (794,668):
                self.knight.targetPos = (949, 568)
            if (self.knight.position - self.knight.targetPos).length() <= 3 and self.knight.targetPos == (814, 568):
                self.knight.targetPos = (794, 924)

        distance = (self.knight.position - self.knight.targetPos).length()

        self.knight.velocity = self.knight.targetPos - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
        if nearest_opponent is not None:
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                    self.knight.target = nearest_opponent
                    return "attacking"

    
    def entry_actions(self):

        self.knight.target = None