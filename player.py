import pygame
import math
import character
import config
import pygame
class Player(character.Character):
    def __init__(self, name, grounds, debug = False):
        self.name = name
        character.Character.__init__(self, grounds, debug, color = (0, 0, 0))
        self.framedict = {}
        initdict(self.framedict)
    def key(self, net):
        keys = pygame.key.get_pressed()
        if config.controller:
            axis = config.controller.get_axis(0)
        else:
            axis = 0
            modifier = 1
        if abs(axis) - 0.4 < 0 :
            axis = 0
            modifier = 1
        if keys[pygame.K_a] or axis < 0:
            if axis == 0:
                net.set_send('Modifier', modifier)
            else:
                modifier =int(abs(axis*10))/10
                net.set_send('Modifier', modifier)
            self.gotoleft(modifier)
            self.framedict['run']['is'] = True
            net.set_send('Left', True)
            net.set_send('Right', False)
        elif keys[pygame.K_d] or axis > 0:
            self.framedict['run']['is'] = True
            if axis == 0:
                net.set_send('Modifier', modifier)
            else:
                modifier = int(abs(axis*10))/10
                net.set_send('Modifier', modifier)
            self.gotoright(modifier)
            net.set_send('Right', True)
            net.set_send('Left', False)
        else:
            self.stopx()
            net.set_send('Right', False)
            net.set_send('Left', False)


    def update_framedict_from_animation(self):
        """Sync framedict with animation state for network transmission"""
        self.framedict["run"]["is"] = self.animation["run"]["is"]
        self.framedict["run"]["sprite"] = self.animation["run"]["sprite"]
        self.framedict["jump"]["is"] = self.animation["jump"]["is"]
        self.framedict["jump"]["sprite"] = self.animation["jump"]["sprite"]
        self.framedict["punch"]["is"] = self.animation["punch"]["is"]
        self.framedict["punch"]["sprite"] = self.animation["punch"]["sprite"]
        self.framedict["uppunch"]["is"] = self.animation["uppunch"]["is"]
        self.framedict["uppunch"]["sprite"] = self.animation["uppunch"]["sprite"]
        self.framedict["midkick"]["is"] = self.animation["midkick"]["is"]
        self.framedict["midkick"]["sprite"] = self.animation["midkick"]["sprite"]
        self.framedict["lowkick"]["is"] = self.animation["lowkick"]["is"]
        self.framedict["lowkick"]["sprite"] = self.animation["lowkick"]["sprite"]
        self.framedict["static"]["is"] = self.animation["static"]["is"]
        self.framedict["static"]["sprite"] = self.animation["static"]["sprite"]
        self.framedict["shield"]["is"] = self.animation['shield']['is']
        self.framedict["shield"]["sprite"] = self.animation['shield']['sprite']
        
    def movementupdate(self, net, enemy=None ):
        character.Character.movementupdate(self, net, enemy=enemy)
        self.update_framedict_from_animation()
        net.set_position(self.position.copy())
        net.set_send('Framedict', self.framedict)
        net.set_send('Velocity', [self.xvelocity, self.yvelocity])
        net.set_send('Facing_right', self.facing_right)
        net.set_send('Jump', False)
        net.set_send("Percentage", self.percentage)
        net.set_send("Stock", self.stock)
        
class DistantPlayer(character.Character):
    def __init__(self, name, grounds):
        self.name = name
        character.Character.__init__(self, grounds, (255, 0, 0), debug=False)
        self.position = [600, -400]
        self.target_position = [600, -400]
        self.last_velocity = [0, 0]

    def key(self, key):
        pass
    def movementupdate(self, net, enemy=None):
        remote_data = net.get_received()
        remote_pos = remote_data.get("Position")
        remote_vel = remote_data.get("Velocity", [0, 0])
        remote_stock = remote_data.get("Stock", 3)
        remote_modifier = remote_data.get("Modifier")
        self.stock = remote_stock
        if remote_pos and remote_pos != [0, 0]:
            self.target_position = remote_pos.copy()
            self.last_velocity = remote_vel if remote_vel else [0, 0]

        lerp_factor = 0.5
        # Update animation from remote framedict
        self.facing_right = remote_data.get("Facing_right")
        remote_framedict = remote_data.get("Framedict")
        if remote_framedict:
            filldict(self.animation, remote_framedict)        
            if remote_framedict['run']['is']:
                if self.facing_right:
                    self.gotoright(remote_modifier)
                else:
                    self.gotoleft(remote_modifier)
                    # Update shield state from remote data
        character.Character.movementupdate(self, net = None, enemy = enemy)
        self.position[0] += int((self.target_position[0] - self.position[0]) * lerp_factor)
        self.position[1] += int((self.target_position[1] - self.position[1]) * lerp_factor)
        self.percentage = remote_data.get("Percentage")
        # Update velocity based on remote data for physics calculations
        self.xvelocity = self.last_velocity[0]
        self.yvelocity = self.last_velocity[1]
 
def initdict(framedict):
    framedict["run"] = {}
    framedict["run"]['is'] = False
    framedict["run"]['sprite'] = 0
    framedict["jump"] = {}
    framedict["jump"]['is'] = False
    framedict["jump"]['sprite'] = 0
    framedict["punch"] = {}
    framedict["punch"]['is'] = False
    framedict["punch"]['sprite'] = 0
    framedict["uppunch"] = {}
    framedict["uppunch"]['is'] = False
    framedict["uppunch"]['sprite'] = 0
    framedict["midkick"] = {}
    framedict["midkick"]['is'] = False
    framedict["midkick"]['sprite'] = 0
    framedict["lowkick"] = {}
    framedict["lowkick"]['is'] = False
    framedict["lowkick"]['sprite'] = 0
    framedict["static"] = {}
    framedict["static"]['is'] = False
    framedict["static"]['sprite'] = 0
    framedict["shield"] = {}
    framedict["shield"]['is'] = False
    framedict["shield"]['sprite'] = 0
def filldict(dict1, dict2):
    dict1["run"]['is'] = dict2["run"]['is']
    dict1["run"]['sprite'] = dict2["run"]['sprite']
    dict1["jump"]['is'] = dict2["jump"]['is']
    dict1["jump"]['sprite'] = dict2["jump"]['sprite']
    dict1["punch"]['is'] = dict2["punch"]['is']
    dict1["punch"]['sprite'] = dict2["punch"]['sprite']
    dict1["uppunch"]['is'] = dict2["uppunch"]['is']
    dict1["uppunch"]['sprite'] = dict2["uppunch"]['sprite']
    dict1["midkick"]['is'] = dict2["midkick"]['is']
    dict1["midkick"]['sprite'] = dict2["midkick"]['sprite']
    dict1["lowkick"]['is'] = dict2["lowkick"]['is']
    dict1["lowkick"]['sprite'] = dict2["lowkick"]['sprite']
    dict1["static"]['is'] = dict2["static"]['is']
    dict1["static"]['sprite'] = dict2["static"]['sprite']
    dict1["shield"]['is'] = dict2["shield"]['is']
    dict1["shield"]['sprite'] = dict2["shield"]['sprite']
