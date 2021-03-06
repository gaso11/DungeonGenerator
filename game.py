import pygame
import tcod
import constant
import math
import pickle
import gzip
import random
import time
import datetime
import os


class Tile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False


class Preferences:

    def __init__(self):

        self.soundVol = .5
        self.musicVol = .5


class Assets:
    def __init__(self):

        self.sndList = []

        self.adjustSound()

        # Load everything!

        # Sheets
        self.players = SpriteSheet("data/graphics/characters/player.png")
        self.undead = SpriteSheet("data/graphics/characters/undead.png")
        self.enemies = SpriteSheet("data/graphics/characters/reptile.png")
        self.walls = SpriteSheet("data/graphics/objects/wall.png")
        self.floors = SpriteSheet("data/graphics/objects/floor.png")
        self.shortWeps = SpriteSheet("data/graphics/items/ShortWep.png")
        self.shields = SpriteSheet("data/graphics/items/Shield.png")
        self.scrolls = SpriteSheet("data/graphics/items/Scroll.png")
        self.flesh = SpriteSheet("data/graphics/items/Flesh.png")
        self.food = SpriteSheet("data/graphics/items/Food.png")
        self.tile = SpriteSheet("data/graphics/objects/tile.png")
        self.misc = SpriteSheet("data/graphics/Items/Light.png")
        self.doors = SpriteSheet("data/graphics/objects/door.png")
        self.stuff = SpriteSheet("data/graphics/objects/decor.png")

        # Animations
        self.player = self.players.getAnimation('m', 4, 16, 16, 2, (32, 32))
        self.snake1 = self.enemies.getAnimation('a', 5, 16, 16, 4, (32, 32))
        self.snake2 = self.enemies.getAnimation('k', 5, 16, 16, 2, (32, 32))
        self.playerGhost = self.undead.getAnimation('e', 5, 16, 16, 2, (32, 32))
        self.doorOpened = self.doors.getAnimation('k', 6, 16, 16, 2, (32, 32))

        # Sprites
        self.wall = self.walls.getImage('d', 4, 16, 16, (32, 32))[0]
        self.wallSeen = self.walls.getImage('d', 13, 16, 16, (32, 32))[0]
        self.floor = self.floors.getImage('b', 5, 16, 16, (32, 32))[0]
        self.floorSeen = self.floors.getImage('b', 14, 16, 16, (32, 32))[0]
        self.sword = self.shortWeps.getImage('a', 2, 16, 16, (32, 32))
        self.shield = self.shields.getImage('a', 1, 16, 16, (32, 32))
        self.lightScroll = self.scrolls.getImage('e', 1, 16, 16, (32, 32))
        self.fireScroll = self.scrolls.getImage('c', 2, 16, 16, (32, 32))
        self.confuseScroll = self.scrolls.getImage('d', 6, 16, 16, (32, 32))
        self.deadSnake = self.flesh.getImage('b', 4, 16, 16, (32, 32))
        self.carrot = self.food.getImage('a', 4, 16, 16, (32, 32))
        self.upStairs = self.tile.getImage('e', 2, 16, 16, (32, 32))
        self.downStairs = self.tile.getImage('f', 2, 16, 16, (32, 32))
        self.magicLamp = self.misc.getImage('e', 1, 16, 16, (32, 32))
        self.doorClosed = self.doors.getImage('j', 6, 16, 16, (32, 32))
        self.sign = self.stuff.getImage('c', 18, 16, 16, (32, 32))

        # Backgrounds
        self.mainMenuBG = pygame.image.load("data/graphics/tower.jpg")
        self.title = pygame.image.load("data/graphics/title.png")
        self.title1 = pygame.image.load("data/graphics/title1.png")
        self.title2 = pygame.image.load("data/graphics/title2.png")
        self.title3 = pygame.image.load("data/graphics/title3.png")
        self.title4 = pygame.image.load("data/graphics/title4.png")
        self.title5 = pygame.image.load("data/graphics/title5.png")
        self.youdied = pygame.image.load("data/graphics/youdiedtest.png")

        # Just in case someone changes the camera size (please don't do that)
        self.mainMenuBG = pygame.transform.scale(self.mainMenuBG, (constant.cameraWidth, constant.cameraHeight))
        self.youdied = pygame.transform.scale(self.youdied, (constant.cameraWidth, constant.cameraHeight))

        self.aniDict = {

            "player" : self.player,
            "snake1" : self.snake1,
            "snake2" : self.snake2,
            "sword" : self.sword,
            "shield" : self.shield,
            "lightScroll" : self.lightScroll,
            "fireScroll" : self.fireScroll,
            "confuseScroll" : self.confuseScroll,
            "carrot" : self.carrot,
            "flesh1" : self.deadSnake,
            "upStairs" : self.upStairs,
            "downStairs" : self.downStairs,
            "magicLamp" : self.magicLamp,
            "doorClosed" : self.doorClosed,
            "doorOpened": self.doorOpened,
            "sign" : self.sign
        }

        tcod.namegen_parse("data/namegen/jice_celtic.cfg")

        # Audio
        self.bgMusic = "data/audio/vortex.mp3"
        self.bgGame = "data/audio/game.mp3"
        self.hit1 = self.addSound("data/audio/hit1.wav")
        self.hit2 = self.addSound("data/audio/hit2.wav")
        self.hit3 = self.addSound("data/audio/hit3.wav")
        self.hit4 = self.addSound("data/audio/hit4.wav")
        self.death = self.addSound("data/audio/death.wav")

        self.hitList = [self.hit1, self.hit2, self.hit3, self.hit4]

    def addSound(self, file):

        sound = pygame.mixer.Sound(file)
        self.sndList.append(sound)

        return sound

    def adjustSound(self):

        for sound in self.sndList:
            sound.set_volume(preferences.soundVol)

        pygame.mixer.music.set_volume(preferences.musicVol)


class Actor:
    def __init__(self, x, y, name, animationKey, animateSpeed=.5,
                 creature=None, ai=None, container=None, item=None, equipment=None,
                 stairs=None, depth=0, state=None, exitportal=None):
        self.x = x
        self.y = y
        self.name = name
        self.animationKey = animationKey
        self.animation = asset.aniDict[self.animationKey]
        self.animateSpeed = animateSpeed / 1.0  # It demands a float
        self.depth = depth
        self.state = state

        self.flickerSpeed = self.animateSpeed / len(self.animation)
        self.flickerTimer = 0.0
        self.spriteImage = 0

        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self

            self.item = Item()
            self.item.owner = self

        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self

        self.exitportal = exitportal
        if self.exitportal:
            self.exitportal.owner = self

    @property
    def displayName(self):
        if self.creature:
            return self.creature.name + "the" + self.name

        if self.item:
            if self.equipment and self.equipment.equipped:
                return self.name + " (E)"
            else:
                return self.name

    def draw(self):
        isVisible = tcod.map_is_in_fov(mapFov, self.x, self.y)

        if isVisible:
            if len(self.animation) == 1:
                mapSurface.blit(self.animation[0], (self.x * constant.cellWidth, self.y * constant.cellHeight))
            elif len(self.animation) > 1:
                if clock.get_fps() > 0.0:
                    self.flickerTimer += 1 / clock.get_fps()

                if self.flickerTimer >= self.flickerSpeed:
                    self.flickerTimer = 0.0

                    if self.spriteImage >= len(self.animation) - 1:
                        self.spriteImage = 0
                    else:
                        self.spriteImage += 1
                mapSurface.blit(self.animation[self.spriteImage],
                                 (self.x * constant.cellWidth, self.y * constant.cellHeight))

    def distanceTo(self, other):

        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx ** 2 + dy ** 2)

    def moveTo(self, other):

        dx = other.x - self.x
        dy = other.y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        self.creature.move(dx, dy)

    def destroy(self):

        self.animation = None

    def resurrect(self):

        self.animation = asset.aniDict[self.animationKey]


dLvl = 1  # which floor you are on


class GameObject:
    def __init__(self):
        self.currentObjects = []
        self.messageHistory = []
        self.prevMaps = []
        self.nextMaps = []
        self.currentMap, self.currentRooms = createMap()

    def nextMap(self):
        global calcFov
        global dLvl

        # Set Fov again
        calcFov = True
        dLvl = dLvl + 1

        for obj in self.currentObjects:
            obj.destroy()

        # Save before leaving
        self.prevMaps.append((player.x, player.y, self.currentMap,
                              self.currentRooms, self.currentObjects))

        if len(self.nextMaps) == 0:

            # Remove Objects from previous level
            self.currentObjects = [player]

            player.resurrect()

            # Re-populate map
            self.currentMap, self.currentRooms = createMap()
            placeObjects(self.currentRooms)
        else:
            (player.x, player.y, self.currentMap,
             self.currentRooms, self.currentObjects) = self.nextMaps[-1]

            for obj in self.currentObjects:
                obj.resurrect()

            makeMapFov(self.currentMap)

            calcFov = True

            # Current map doesn't need to be in the list anymore
            # unless you like being trapped on one floor
            del self.nextMaps[-1]

    def prevMap(self):
        global calcFov
        global dLvl

        if len(self.prevMaps) != 0:

            for obj in self.currentObjects:
                obj.destroy()

            # Save before going back
            self.nextMaps.append((player.x, player.y, self.currentMap,
                                  self.currentRooms, self.currentObjects))

            (player.x, player.y, self.currentMap,
             self.currentRooms, self.currentObjects) = self.prevMaps[-1]

            for obj in self.currentObjects:
                obj.resurrect()

            makeMapFov(self.currentMap)

            calcFov = True
            dLvl = dLvl - 1

            # Delete floor while you're here, or you'll be trapped like in nextMap
            del self.prevMaps[-1]


class SpriteSheet:
    def __init__(self, fileName):
        self.spriteSheet = pygame.image.load(fileName).convert()
        self.tileDict = {'a': 1, 'b': 2, 'c': 3, 'd': 4,
                         'e': 5, 'f': 6, 'g': 7, 'h': 8,
                         'i': 9, 'j': 10, 'k': 11, 'l': 12,
                         'm': 13, 'n': 14, 'o': 15, 'p': 16}

    def getImage(self, col, row, width=constant.cellWidth,
                 height=constant.cellHeight, scale=None):

        imageList = []

        image = pygame.Surface([width, height]).convert()
        image.blit(self.spriteSheet, (0, 0), (self.tileDict[col] * width, row * height, width, height))
        image.set_colorkey(constant.colorBlack)

        if scale:
            (newWidth, newHeight) = scale
            image = pygame.transform.scale(image, (newWidth, newHeight))

        imageList.append(image)

        return imageList

    def getAnimation(self, col, row, width=constant.cellWidth,
                 height=constant.cellHeight, numSprites=1, scale=None):

        imageList = []

        for i in range(numSprites):
            image = pygame.Surface([width, height]).convert()
            image.blit(self.spriteSheet, (0, 0), (self.tileDict[col] * width + (width * i), row * height, width, height))
            image.set_colorkey(constant.colorBlack)

            if scale:
                (newWidth, newHeight) = scale
                image = pygame.transform.scale(image, (newWidth, newHeight))

            imageList.append(image)

        return imageList


class Room:

    def __init__(self, coords, size):
        self.x1, self.y1 = coords
        self.w, self.h = size
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

    @property
    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2

        return (center_x, center_y)

    def intersect(self, other):

        objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

        return objects_intersect


class Camera:

    def __init__(self):

        self.width = constant.cameraWidth
        self.height = constant.cameraHeight
        self.x, self.y = (0, 0)

    @property
    def rectangle(self):

        pos = pygame.Rect((0, 0), (constant.cameraWidth, constant.cameraHeight))

        pos.center = (self.x, self.y)

        return pos

    @property
    def mapAddress(self):

        mapX = self.x // constant.cellWidth
        mapY = self.y // constant.cellHeight

        return mapX, mapY

    def update(self):

        targetX = player.x * constant.cellWidth + (constant.cellWidth // 2)
        targetY = player.y * constant.cellHeight + (constant.cellHeight // 2)
        distX, distY = self.mapDist((targetX, targetY))

        self.x += int(distX * constant.cameraSpeed)
        self.y += int(distY * constant.cameraSpeed)

    def winMap(self, coords):

        x, y = coords

        # Convert Window coords to camera coords
        camX, camY = self.camDist((x, y))

        mapX = self.x + camX
        mapY = self.y + camY

        return mapX, mapY

    def mapDist(self, coords):

        x, y = coords
        distX = x - self.x
        distY = y - self.y

        return distX, distY

    def camDist(self, coords):

        x, y = coords
        distX = x - (self.width // 2)
        distY = y - (self.height // 2)

        return distX, distY


class Creature:
    def __init__(self, name, baseAttack=2, baseDefense=0, hp=30, deathFunction = None):
        self.name = name
        self.baseAttack = baseAttack
        self.baseDefense = baseDefense
        self.maxHp = hp
        self.hp = hp
        self.deathFunction = deathFunction

    def move(self, dx, dy):

        tileIsWall = (game.currentMap[self.owner.x + dx][self.owner.y + dy].blockPath == True)

        target = checkMapForCreatures(self.owner.x + dx, self.owner.y + dy, self.owner)

        if target:
            self.attack(target)

        if not tileIsWall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target):

        damage = self.power - target.creature.defense
        gameMessage(self.name + " attacks " + target.creature.name + " for " + str(damage) + " damage!", constant.colorWhite)

        target.creature.takeDamage(damage)
        if target == player and player.creature.hp <= 0:
            deathPlayer(player)

        if damage > 0 and self.owner is player:
            pygame.mixer.Sound.play(randomness.choice(asset.hitList))

    def takeDamage(self, damage):
        if damage <= 0:
            damage = 1

        self.hp -= damage
        gameMessage(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp), constant.colorRed)

        if self.hp <= 0:
            if self.deathFunction is not None:
                self.deathFunction(self.owner)

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.maxHp:
            self.hp = self.maxHp

    @property
    def power(self):

        totalPower = self.baseAttack

        if self.owner.container:
            bonuses = [obj.equipment.attackBonus
                       for obj in self.owner.container.equippedItems]

            for bonus in bonuses:
                if bonus:
                    totalPower += bonus

        return totalPower

    @property
    def defense(self):
        totalDefense = self.baseDefense

        if self.owner.container:
            bonuses = [obj.equipment.defenseBonus
                       for obj in self.owner.container.equippedItems]

            for bonus in bonuses:
                if bonus:
                    totalDefense += bonus

        return totalDefense


class Item:
    def __init__(self, weight = 0.0, volume = 0.0, use_function=None, value=None):
        self.weight = weight
        self.volume = volume
        self.use_function = use_function
        self.value = value

    def pickUp(self, actor):
        if actor.container:
            if actor.container.volume + self.volume > actor.container.maxVol:
                gameMessage("Not enough room to pick up!", constant.colorRed)
            else:
                gameMessage("Picking up!", constant.colorRed)
                actor.container.inventory.append(self.owner)
                self.owner.destroy()
                game.currentObjects.remove(self.owner)
                self.container = actor.container

    def drop(self, x, y):
        game.currentObjects.append(self.owner)

        self.owner.resurrect()

        self.container.inventory.remove(self.owner)
        self.owner.x = x
        self.owner.y = y
        gameMessage("Item Dropped!", constant.colorRed)

    def use(self):

        if self.owner.equipment:
            self.owner.equipment.toggleEquip()
            return

        if self.use_function:
            result = self.use_function(self.container.owner, self.value)

            if result is not None:
                print("Use function failed")

            else:
                self.container.inventory.remove(self.owner)


class Equipment:

    def __init__(self, attackBonus=None, defenseBonus=None, slot=None):
        self.attackBonus = attackBonus
        self.defenseBonus = defenseBonus
        self.slot = slot

        self.equipped = False

    def toggleEquip(self):

        if self.equipped:
            self.unequip()
        else:
            self.equip()

    def equip(self):

        equippedItems = self.owner.item.container.equippedItems

        for item in equippedItems:
            if item.equipment.slot and item.equipment.slot == self.slot:
                gameMessage("Equipment slot is occupied", constant.colorRed)
                return

        self.equipped = True
        gameMessage("Item equipped!")

    def unequip(self):
        self.equipped = False
        gameMessage("Item unequipped!")


class Stairs:

    def __init__(self, up=True):

        self.up = up

    def use(self):
        if self.up:
            game.nextMap()
        else:
            game.prevMap()


class ExitDoor:
    def __init__(self):
        self.opening = "doorOpened"
        self.closing = "doorClosed"

    def update(self):

        foundLamp = False

        isOpen = self.owner.state == "Open"

        for obj in player.container.inventory:
            if obj.name == "The Lamp":
                foundLamp = True

        if foundLamp and not isOpen:
            self.owner.state = "Open"
            self.owner.animationKey = self.opening
            self.owner.resurrect()

        if not foundLamp and isOpen:
            self.owner.state = "Closed"
            self.owner.animationKey = self.closing
            self.owner.resurrect()

    def use(self):

        if self.owner.state == "Open":
            player.state = "win"
            mainSurface.fill(constant.colorWhite)
            center = (constant.cameraWidth/2, constant.cameraHeight/2)

            drawText(mainSurface, "YOU WIN!", constant.titleFont, center, constant.colorBlack, center=True)

            pygame.display.update()

            pygame.time.wait(3000)


class Container:
    def __init__(self, volume = 10.0, inventory = None):
        self.inventory = inventory
        self.maxVol = volume
        if inventory:
            self.inventory = inventory
        else:
            self.inventory = []

    @property
    def volume(self):
        return 0.0

    @property
    def equippedItems(self):

        equippedList = [obj for obj in self.inventory
                        if obj.equipment and obj.equipment.equipped]

        return equippedList


class AIConfuse:

    def __init__(self, oldAI, turns):

        self.oldAI = oldAI
        self.turns = turns

    def takeTurn(self):

        if self.turns > 0:
            self.owner.creature.move(tcod.random_get_int(None, -1, 1),
                                    tcod.random_get_int(None, -1, 1))

            self.turns -= 1
        else:
            self.owner.ai = self.oldAI
            gameMessage(self.owner.displayName + " is no longer confused", constant.colorRed)


class AIChase:

    def takeTurn(self):
        monster = self.owner

        if tcod.map_is_in_fov(mapFov, monster.x, monster.y):
            if monster.distanceTo(player) >= 2:
                self.owner.moveTo(player)

            elif player.creature.hp > 0:
                monster.creature.attack(player)


def deathPlayer(player):

    player.state = "DEAD"
    player.creature.hp = 0
    player.animation = asset.playerGhost
    youdied = asset.youdied

    mainSurface.blit(youdied, (0, 0))
    pygame.mixer.Sound.play(asset.death)

    pygame.display.update()

    filename = ("data\playerInfo\\" + player.creature.name + "." +
                datetime.date.today().strftime("%Y%B%d"))

    deathFile = open(filename, 'a+')

    for message, color in game.messageHistory:
        deathFile.write(message + "\n")

    pygame.time.wait(3000)


def deathSnake(monster):
    gameMessage(monster.creature.name + " is dead!", constant.colorGrey)

    monster.animation = asset.deadSnake
    monster.depth = constant.corpseDepth
    monster.animationKey = "flesh1"
    monster.creature = None
    monster.ai = None


def createMap():
    new_map = [[Tile(True) for y in range(0, constant.mapHeight)] for x in range(0, constant.mapWidth)]

    list_of_rooms = []

    for i in range(constant.mapMaxNumRooms):

        w = tcod.random_get_int(0, constant.roomMinWidth, constant.roomMaxWidth)
        h = tcod.random_get_int(0, constant.roomMinHeight, constant.roomMaxHeight)
        x = tcod.random_get_int(0, 2, constant.mapWidth - w - 2)
        y = tcod.random_get_int(0, 2, constant.mapHeight - h - 2)

        new_room = Room((x, y), (w, h))

        failed = False

        for other_room in list_of_rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            map_create_room(new_map, new_room)
            current_center = new_room.center

            if len(list_of_rooms) != 0:

                previous_center = list_of_rooms[-1].center

                map_create_tunnels(current_center, previous_center, new_map)

            list_of_rooms.append(new_room)

    makeMapFov(new_map)

    return new_map, list_of_rooms


def placeObjects(roomList):

    currentLevel = len(game.prevMaps) + 1

    firstLevel = (currentLevel == 1)
    finalLevel = (currentLevel == constant.mapLevels)

    for room in roomList:

        firstRoom = (room == roomList[0])
        lastRoom = (room == roomList[-1])

        if firstRoom:
            player.x, player.y = room.center

        if firstRoom and firstLevel:
            genDoor(room.center)
            genSign((player.x + 1, player.y - 1))

        if firstRoom and not firstLevel:
            genStairs((player.x, player.y), up=False)

        if lastRoom:
            if finalLevel:
                genLamp(room.center)
            else:
                genStairs(room.center)



        # Get random coords inside the room
        x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # Place enemies and Items
        genEnemy((x, y))

        x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        genItem((x, y))


def map_create_room(new_map, new_room):
    for x in range(new_room.x1, new_room.x2):
        for y in range(new_room.y1, new_room.y2):
            new_map[x][y].blockPath = False


def map_create_tunnels(coords1, coords2, new_map):

    coin_flip = (tcod.random_get_int(0, 0, 1) == 1)

    x1, y1 = coords1
    x2, y2 = coords2

    if coin_flip:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y1].blockPath = False
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[x2][y].blockPath = False
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[x1][y].blockPath = False
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[x][y2].blockPath = False


def checkMapForCreatures(x, y, excludeObj = None):

    target = None

    if excludeObj:
        for obj in game.currentObjects:
            if (obj is not excludeObj and obj.x == x and obj.y == y and obj.creature):
                target = obj

        if target:
            return target

    else:
        for obj in game.currentObjects:
            if (obj.x == x and obj.y == y and obj.creature):
                target = obj
                return target


def makeMapFov(pMap):
    global mapFov

    mapFov = tcod.map_new(constant.mapWidth, constant.mapHeight)

    for y in range(constant.mapHeight):
        for x in range(constant.mapWidth):
            tcod.map_set_properties(mapFov, x, y,
                                    not pMap[x][y].blockPath, not pMap[x][y].blockPath)


def calculateMapFov():
    global calcFov

    if calcFov:
        calcFov = False
        tcod.map_compute_fov(mapFov, player.x, player.y,
                             constant.radius, constant.lightWalls, constant.algoFov)


def objectsAtCoords(x, y):
    options = [obj for obj in game.currentObjects if obj
               if obj.x == x and obj.y == y]

    return options


def findLine(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2

    tcod.line_init(x1, y1, x2, y2)

    calcX, calcY = tcod.line_step()

    coordList = []

    if x1 == x2 and y1 == y2:
        return [(x1, y1)]

    while (not calcX is None):
        coordList.append((calcX, calcY))

        calcX, calcY = tcod.line_step()

    return coordList


def findRadius(coords, radius):

    centerX, centerY = coords
    list = []

    for x in range((centerX - radius), centerX + radius + 1):
        for y in range((centerY - radius), centerY + radius + 1):
            list.append((x, y))

    return list


def drawMap(toDraw):

    # Frames drop after a while because of how much you explore the map, this fixes that
    camX, camY = camera.mapAddress
    mapW = constant.cameraWidth // constant.cellWidth
    mapH = constant.cameraHeight // constant.cellHeight

    renderWMin = camX - (mapW // 2)
    renderHMin = camY - (mapH // 2)
    renderWMax = camX + (mapW // 2)
    renderHMax = camY + (mapH // 2)

    if renderWMin < 0:
        renderWMin = 0

    if renderHMin < 0:
        renderHMin = 0

    if renderWMax > constant.mapWidth:
        renderWMax = constant.mapWidth

    if renderHMax > constant.mapHeight:
        renderHMax = constant.mapHeight

    for x in range(renderWMin, renderWMax):
        for y in range(renderHMin, renderHMax):

            isVisible = tcod.map_is_in_fov(mapFov, x, y)

            if isVisible:

                toDraw[x][y].explored = True

                if toDraw[x][y].blockPath == True:
                    # wall
                    mapSurface.blit(asset.wall, (x * constant.cellWidth, y * constant.cellHeight))
                else:
                    # floor
                    mapSurface.blit(asset.floor, (x * constant.cellWidth, y * constant.cellHeight))

            elif toDraw[x][y].explored:
                if toDraw[x][y].blockPath == True:
                    # wall
                    mapSurface.blit(asset.wallSeen, (x * constant.cellWidth, y * constant.cellHeight))
                else:
                    # floor
                     mapSurface.blit(asset.floorSeen, (x * constant.cellWidth, y * constant.cellHeight))


def draw():
    global mainSurface

    # clear
    mainSurface.fill(constant.colorDefaultBG)
    mapSurface.fill(constant.colorDefaultBG)

    camera.update()

    # map
    drawMap(game.currentMap)

    # character
    for obj in sorted(game.currentObjects, key=lambda objs: objs.depth, reverse=True):
        obj.draw()

    mainSurface.blit(mapSurface, (0, 0), camera.rectangle)

    drawDebug()
    drawMessages()


def drawDebug():
    global dLvl

    drawText(mainSurface, "health: " + str(int(player.creature.hp)),
             constant.debugFont,
             (constant.cameraWidth-180, constant.cameraHeight-60),
             constant.colorWhite, constant.colorBlack)

    drawText(mainSurface, "level: " + str(int(dLvl)),
             constant.debugFont,
             (constant.cameraWidth-180, constant.cameraHeight-30),
             constant.colorWhite, constant.colorBlack)


def drawMessages():
    if len(game.messageHistory) <= constant.numMessages:
        toDraw = game.messageHistory
    else:
        toDraw = game.messageHistory[-constant.numMessages:]

    textHeight = helperTextHeight(constant.messageTextFont)

    startY = (constant.cameraHeight - (constant.numMessages * textHeight)) - 5

    i = 0

    for message, color in toDraw:

        drawText(mainSurface, message, constant.messageTextFont, (0, startY + (i * textHeight)),
                 color, constant.colorBlack)

        i += 1


def drawTileRect(coords, tileColor=None, tileAlpha=None, mark=None):

    x, y = coords

    if tileColor:
        color = tileColor
    else:
        color = constant.colorWhite

    if tileAlpha:
        alpha = tileAlpha
    else:
        alpha = 150

    x = x * constant.cellWidth
    y = y * constant.cellHeight

    selSurface = pygame.Surface((constant.cellWidth, constant.cellHeight))
    selSurface.fill(color)
    selSurface.set_alpha(alpha)

    # Does not display mark correctly
    if mark:
        drawText(selSurface, mark, font=constant.cursorFont,
                 coord=(constant.cellWidth/2, constant.cellHeight/2),
                 color=constant.colorBlack, center=True)
    mapSurface.blit(selSurface, (x, y))


def drawText(surface, text, font, coord, color, background = None, center=False):
    textSurf, textRect = helperTextObj(text, font, color, background)

    if not center:
        textRect.topleft = coord
    else:
        textRect.center = coord

    surface.blit(textSurf, textRect)


def helperTextObj(text, font, color, background):

    if background:
        surfaceText = font.render(text, False, color, background)
    else:
        surfaceText = font.render(text, False, color)

    return surfaceText, surfaceText.get_rect()


def helperTextHeight(font):

    fontObj = font.render('a', False, (0, 0, 0))
    fontRect = fontObj.get_rect()

    return fontRect.height


def helperTextWidth(font):

    fontObj = font.render('a', False, (0, 0, 0))
    fontRect = fontObj.get_rect()

    return fontRect.width


def castHeal(target, value):

    if target.creature.hp == target.creature.maxHp:
        gameMessage(target.creature.name + " the " + target.name +
              " is already at full health!", constant.colorWhite)
        return "canceled"
    else:
        gameMessage(target.creature.name + " the " + target.name +
              " healed for " + str(value), constant.colorWhite)
        target.creature.heal(value)

    return None


def castLightning(caster, values):

    damage, mrange = values

    point = menuSelectTarget(origin=(caster.x, caster.y), range=mrange, penWall=False)

    if point:
        tileList = findLine((player.x, player.y), point)

        for i, (x, y) in enumerate(tileList):
            target = checkMapForCreatures(x, y)

            if target:
                target.creature.takeDamage(damage)


def castFire(caster, values):

    damage, radius, mrange = values

    point = menuSelectTarget(origin=(caster.x, caster.y), range=mrange,
                             penWall=False, penCreat=True, radius=radius)

    if point:
        damageTiles = findRadius(point, radius)

        hit = False

        for (x, y) in damageTiles:
            target = checkMapForCreatures(x, y)

            if target:
                target.creature.takeDamage(damage)

                if target is not player:
                    hit = True

        if hit:
            gameMessage("Fireball used on monster!", constant.colorRed)


def castConfusion(caster, turns):

    point = menuSelectTarget()

    if point:
        x, y = point
        target = checkMapForCreatures(x, y)

        if target:
            oldAI = target.ai

            target.ai = AIConfuse(oldAI=oldAI, turns=turns)
            target.ai.owner = target

            gameMessage("The creatures are confused!", constant.colorGreen)


def readSign(caster, value):
    print("Sign has been read")
    width = 480
    height = 100
    windowWidth = constant.cameraWidth
    windowHeight = constant.cameraHeight
    menuX = (windowWidth / 2) - (width / 2)
    menuY = (windowHeight / 2) - (height / 2)
    isClosed = False

    signSurface = pygame.Surface((width, height))

    while not isClosed:
        signSurface.fill(constant.colorBlack)

        eventsList = pygame.event.get()

        for event in eventsList:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    isClosed = True

        drawText(signSurface,
                 "Snakes have poor vision, this makes it hard to",
                 constant.messageTextFont, (0, 0), color=constant.colorWhite)

        drawText(signSurface,
                 "follow people around corners...hint hint",
                 constant.messageTextFont, (0, 15), color=constant.colorWhite)

        drawText(signSurface,
                 "Game made by Evan, Tyler, George",
                 constant.messageTextFont, (0, 80), color=constant.colorWhite)

        draw()

        mainSurface.blit(signSurface, (menuX, menuY))

        clock.tick(constant.gameFPS)

        pygame.display.update()


def menuPause():
    isClosed = False

    windowWidth = constant.cameraWidth
    windowHeight = constant.cameraHeight

    menuText = "PAUSED"
    menuFont = constant.debugFont

    textHeight = helperTextHeight(menuFont)
    textWidth = len(menuText) * helperTextWidth(menuFont)

    while not isClosed:
        eventsList = pygame.event.get()

        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    isClosed = True

        drawText(mainSurface, menuText, menuFont,
                 ((windowWidth / 2) - (textWidth / 2), (windowHeight / 2) - (textHeight / 2)),
                 constant.colorWhite, constant.colorBlack)

        clock.tick(constant.gameFPS)

        pygame.display.flip()


class Button:

    def __init__(self, surface, text, size, coords,
                 colorMouseOver=constant.colorRed,
                 colorDefault=constant.colorGreen,
                 colorTextMouse=constant.colorGrey,
                 colorTextDefault=constant.colorGrey):

        self.surface = surface
        self.text = text
        self.size = size
        self.coords = coords
        self.colorMouse = colorMouseOver
        self.colorDefault = colorDefault
        self.colorTextMouse = colorTextMouse
        self.colorTextDefault = colorTextDefault
        self.currentColor = colorDefault
        self.currentTextColor = colorTextDefault

        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = coords

    def update(self, playerInput):

        mouseClicked = False

        levent, mousePos = playerInput
        mouseX, mouseY = mousePos

        mouseOver = (mouseX >= self.rect.left and
                     mouseX <= self.rect.right and
                     mouseY >= self.rect.top and
                     mouseY <= self.rect.bottom)

        for event in levent:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseClicked = True

        if mouseOver and mouseClicked:
            return True

        if mouseOver:
            self.currentColor = self.colorMouse
            self.currentTextColor = self.colorTextMouse
        else:
            self.currentColor = self.colorDefault
            self.currentTextColor = self.colorTextDefault

    def draw(self):

        pygame.draw.rect(self.surface, self.currentColor, self.rect)
        drawText(self.surface, self.text, constant.debugFont,
                 self.coords, self.currentTextColor,
                 center=True)


class Slider:
    def __init__(self, surface, size, coords, bgColor, fgColor, value):

        self.surface = surface
        self.size = size
        self.coords = coords
        self.bgColor = bgColor
        self.fgColor = fgColor
        self.value = value

        self.bgRect = pygame.Rect((0, 0), size)
        self.bgRect.center = coords

        self.fgRect = pygame.Rect((0, 0), (self.bgRect.width * self.value, self.bgRect.height))
        self.fgRect.topleft = self.bgRect.topleft

        self.tab = pygame.Rect((0, 0), (20, self.bgRect.height + 4))
        self.tab.center = (self.fgRect.right, self.bgRect.centery)

    def update(self, sliderInput):

        mouseDown = pygame.mouse.get_pressed()[0]

        levent, mousePos = sliderInput
        mouseX, mouseY = mousePos

        mouseOver = (mouseX >= self.bgRect.left and
                     mouseX <= self.bgRect.right and
                     mouseY >= self.bgRect.top and
                     mouseY <= self.bgRect.bottom)

        if mouseDown and mouseOver:
            self.value = (float(mouseX) - float(self.bgRect.left)) / self.bgRect.width

            self.fgRect.width = self.bgRect.width * self.value
            self.tab.center = (self.fgRect.right, self.bgRect.centery)

    def draw(self):
        pygame.draw.rect(self.surface, self.bgColor, self.bgRect)
        pygame.draw.rect(self.surface, self.fgColor, self.fgRect)
        pygame.draw.rect(self.surface, constant.colorBlack, self.tab)


def mainMenu():

    gameInt()

    menuRunning = True

    titleX = constant.cameraWidth//2
    titleY = constant.cameraHeight//2 - 40
    titleani = [asset.title1, asset.title2, asset.title3, asset.title4, asset.title5]

    # Button Stuff
    continueBY = titleY + 40
    newGameBY = continueBY + 40
    optionsBY = newGameBY + 40
    quitBY = optionsBY + 40

    continueB = Button(mainSurface, "Continue", (200, 30),
                       (constant.cameraWidth//2, continueBY))

    newGameB = Button(mainSurface, "New Game", (200, 30),
                      (constant.cameraWidth // 2, newGameBY))

    optionsB = Button(mainSurface, "Options", (200, 30),
                      (constant.cameraWidth // 2, optionsBY))

    quitB = Button(mainSurface, "Quit Game", (200, 30),
                   (constant.cameraWidth // 2, quitBY))

    pygame.mixer.music.load(asset.bgMusic)
    pygame.mixer.music.play(-1)

    i = 0

    while menuRunning:

        eventList = pygame.event.get()
        mousePos = pygame.mouse.get_pos()

        gameInput = (eventList, mousePos)

        # Handle events and buttons
        for event in eventList:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if continueB.update(gameInput):
            pygame.mixer.music.stop()
            # Load game
            pygame.mixer.music.load(asset.bgGame)
            pygame.mixer.music.play(-1)

            try:
                loadGame()
            except:
                newGame()

            gameLoop()

        if newGameB.update(gameInput):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(asset.bgGame)
            pygame.mixer.music.play(-1)
            newGame()
            gameLoop()
            gameInt()

        if optionsB.update(gameInput):
            menuOptions()

        if quitB.update(gameInput):
            pygame.quit()
            exit()

        mainSurface.blit(asset.mainMenuBG, (0, 0))

        if i > 4:
            i = 0

        mainSurface.blit(titleani[i], (150, 180))
        i += 1
        time.sleep(0.1)


        # draw
        continueB.draw()
        newGameB.draw()
        optionsB.draw()
        quitB.draw()

        # update
        pygame.display.update()


def menuOptions():

    width = 200
    height = 200
    bgColor = constant.colorGrey
    center = (constant.cameraWidth // 2, constant.cameraHeight // 2)

    sliderX = constant.cameraWidth//2
    soundSliderY = constant.cameraHeight//2 - 60
    musicSliderY = soundSliderY + 50

    soundTextY = soundSliderY - 20
    musicTextY = musicSliderY - 20

    saveBY = musicSliderY + 50

    optionsSurface = pygame.Surface((width, height))

    menuRect = pygame.Rect(0, 0, width, height)
    menuRect.center = center

    closed = False

    mainSurface.blit(optionsSurface, menuRect.topleft)

    soundSlider = Slider(mainSurface, (125, 15), (sliderX, soundSliderY),
                         constant.colorRed, constant.colorGreen, preferences.soundVol)

    musicSlider = Slider(mainSurface, (125, 15), (sliderX, musicSliderY),
                         constant.colorRed, constant.colorGreen, preferences.musicVol)

    saveB = Button(mainSurface, "Save", (70, 30), (sliderX, saveBY), constant.colorDDGrey,
                   constant.colorDGrey, constant.colorBlack, constant.colorBlack)

    while not closed:

        eventList = pygame.event.get()
        mousePos = pygame.mouse.get_pos()

        gameInput = (eventList, mousePos)

        # Handle events and buttons
        for event in eventList:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    closed = True

        soundVol = preferences.soundVol
        musicVol = preferences.musicVol

        soundSlider.update(gameInput)
        musicSlider.update(gameInput)

        if soundVol is not soundSlider.value:
            preferences.soundVol = soundVol
            asset.adjustSound()

        if musicVol is not musicSlider.value:
            preferences.musicVol = musicVol
            asset.adjustSound()

        if saveB.update(gameInput):
            savePreferences()
            closed = True

        # Start Drawing
        optionsSurface.fill(bgColor)
        mainSurface.blit(optionsSurface, menuRect.topleft)

        drawText(mainSurface, "Sound Volume", constant.debugFont, (sliderX, soundTextY),
                 constant.colorBlack, center=True)

        drawText(mainSurface, "Music Volume", constant.debugFont, (sliderX, musicTextY),
                 constant.colorBlack, center=True)

        soundSlider.draw()
        musicSlider.draw()
        saveB.draw()

        pygame.display.update()


def menuInventory():
    isClosed = False
    menuWidth = 200
    menuHeight = 200
    windowWidth = constant.cameraWidth
    windowHeight = constant.cameraHeight
    menuX = (windowWidth / 2) - (menuWidth / 2)
    menuY = (windowHeight / 2) - (menuHeight / 2)
    menuFont = constant.messageTextFont
    menuTextHeight = helperTextHeight(menuFont)
    color = constant.colorWhite

    invSurface = pygame.Surface((menuWidth, menuHeight))

    while not isClosed:

        invSurface.fill(constant.colorBlack)

        printList = [obj.displayName for obj in player.container.inventory]

        eventsList = pygame.event.get()
        mouseX, mouseY = pygame.mouse.get_pos()
        mouseXRel = mouseX - menuX
        mouseYRel = mouseY - menuY

        mouseInWindow = (mouseXRel >= 0 and
                         mouseYRel >= 0 and
                         mouseXRel <= menuWidth and
                         mouseYRel <= menuHeight)

        mouseSelect = int(mouseYRel / menuTextHeight)

        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    isClosed = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mouseInWindow and mouseSelect <= len(printList) - 1:
                        player.container.inventory[mouseSelect].item.use()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if mouseInWindow and mouseSelect <= len(printList) - 1:
                        player.container.inventory[mouseSelect].item.drop(player.x, player.y)

        for line, (name) in enumerate(printList):
            if line == mouseSelect and mouseInWindow:
                drawText(invSurface, name, menuFont, (0, 0 + (line * menuTextHeight)), color, constant.colorGrey)
            else:
                drawText(invSurface, name, menuFont, (0, 0 + (line * menuTextHeight)), color)

        draw()

        mainSurface.blit(invSurface, (menuX, menuY))

        clock.tick(constant.gameFPS)

        pygame.display.update()


def menuSelectTarget(origin=None, range=None, penWall= True,
                     penCreat = True, radius=None):
    isClosed = False

    while not isClosed:
        mouseX, mouseY = pygame.mouse.get_pos()
        eventList = pygame.event.get()

        mapPX, mapPY = camera.winMap((mouseX, mouseY))

        mapX = int(mapPX / constant.cellWidth)
        mapY = int(mapPY / constant.cellHeight)

        validTiles = []

        if origin:
            tileList = findLine(origin, (mapX, mapY))

            for i, (x, y) in enumerate(tileList):

                validTiles.append((x, y))

                if range and i == range - 1:
                    break

                if not penWall and game.currentMap[x][y].blockPath:
                    break

                if not penCreat and checkMapForCreatures(x, y):
                    break
        else:
            validTiles = [(mapX, mapY)]

        for event in eventList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    isClosed = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return (validTiles[-1])

        mainSurface.fill(constant.colorDefaultBG)
        mapSurface.fill(constant.colorDefaultBG)

        camera.update()

        # map
        drawMap(game.currentMap)

        # character
        for obj in game.currentObjects:
            obj.draw()

        for (tileX, tileY) in validTiles:
            if (tileX, tileY) == validTiles[-1]:
                drawTileRect(coords=(tileX, tileY), mark='X')
            else:
                drawTileRect(coords=(tileX, tileY))

        if radius:
            area = findRadius(validTiles[-1], radius)

            for (tileX, tileY) in area:
                drawTileRect(coords=(tileX, tileY), tileColor=constant.colorRed)

        mainSurface.blit(mapSurface, (0, 0), camera.rectangle)
        drawDebug()
        drawMessages()

        pygame.display.flip()

        clock.tick(constant.gameFPS)


def gen_player(coords):

    global player

    x, y = coords

    # TODO: put player attack and defense to a normal number
    container = Container()
    creature = Creature("Evan", baseAttack=40, baseDefense=40, deathFunction=deathPlayer)
    player = Actor(x, y, "Wizard", "player", animateSpeed=1, creature=creature,
                   container=container)

    game.currentObjects.append(player)


def genStairs(coords, up=True):

    x, y = coords

    if up:
        stairsC = Stairs()
        stairs = Actor(x, y, "stairs", "upStairs", stairs=stairsC,
                       depth=constant.backgroundDepth)
    else:
        stairsC = Stairs(up)
        stairs = Actor(x, y, "stairs", "downStairs", stairs=stairsC,
                       depth=constant.backgroundDepth)

    game.currentObjects.append(stairs)


def genDoor(coords):

    x, y = coords
    dor = ExitDoor()
    door = Actor(x, y, "exit door", animationKey="doorClosed", depth=constant.backgroundDepth,
                 exitportal=dor)

    game.currentObjects.append(door)


def genLamp(coords):

    x, y =coords

    item = Item()

    returnobj = Actor(x, y, "The Lamp", animationKey="magicLamp", depth=constant.itemDepth, item=item)

    game.currentObjects.append(returnobj)


def genSign(coords):
    x, y = coords

    item = Item(use_function=readSign)

    returnobj = Actor(x, y, "Sign", "sign", depth=constant.itemDepth, item=item)

    game.currentObjects.append(returnobj)


def genItem(coords):

    rand = tcod.random_get_int(0, 1, 6)

    if rand == 1:
        item = genLightningScroll(coords)
    elif rand == 2:
        item = genFireballScroll(coords)
    elif rand == 3:
        item = genConfusionScroll(coords)
    elif rand == 4:
        item = genSword(coords)
    elif rand == 5:
        item = genShield(coords)
    elif rand == 6:
        item = genHealth(coords)
    else:
        # This does not affect gameplay, but is here to catch this error
        print("Item creation failed")
        return

    game.currentObjects.append(item)


def genSword(coords):

    x, y = coords

    bonus = tcod.random_get_int(0, 1, 2)

    equipment = Equipment(attackBonus=bonus, slot="rightHand")

    returnItem = Actor(x, y, "Sword", "sword", equipment=equipment,
                       depth=constant.itemDepth)

    return returnItem


def genShield(coords):
    x, y = coords

    bonus = tcod.random_get_int(0, 1, 2)

    equipment = Equipment(defenseBonus=bonus, slot="leftHand")

    returnItem = Actor(x, y, "Shield", "shield", equipment=equipment,
                       depth=constant.itemDepth)

    return returnItem


def genEnemy(coords):
    rand = tcod.random_get_int(0, 1, 100)

    if rand > 15:
        newEnemy = genSnakeBasic(coords)
    elif rand < 15:
        newEnemy = genSnakeHard(coords)
    else:
        print("Item creation failed")
        return

    game.currentObjects.append(newEnemy)


def genSnakeBasic(coords):
    x, y = coords

    health = tcod.random_get_int(0, 5, 10)
    attack = tcod.random_get_int(0, 1, 2)
    name = tcod.namegen_generate("Celtic female")

    creature = Creature(name, deathFunction=deathSnake, hp=health, baseAttack=attack)
    ai1 = AIChase()
    snake = Actor(x, y, "Basic Snake", "snake1",
                  animateSpeed=1, creature=creature, ai=ai1,
                  depth=constant.creatureDepth)

    return snake


def genSnakeHard(coords):
    x, y = coords

    health = tcod.random_get_int(0, 15, 20)
    attack = tcod.random_get_int(0, 3, 6)
    name = tcod.namegen_generate("Celtic male")

    creature = Creature(name, deathFunction=deathSnake, hp=health, baseAttack=attack)
    ai1 = AIChase()
    snake = Actor(x, y, "Hard Snake", "snake2",
                  animateSpeed=1, creature=creature, ai=ai1,
                  depth=constant.creatureDepth)

    # game.currentObjects.append(basicSnake)
    return snake


def genLightningScroll(coords):
    x, y = coords

    damage = tcod.random_get_int(0, 5, 7)
    mrange = tcod.random_get_int(0, 7, 8)

    item = Item(use_function=castLightning, value=(damage, mrange))

    returnItem = Actor(x, y, "Lightning Scroll", "lightScroll", item=item,
                       depth=constant.itemDepth)

    return returnItem


def genFireballScroll(coords):
    x, y = coords

    damage = tcod.random_get_int(0, 2, 4)
    radius = 1
    mrange = tcod.random_get_int(0, 9, 12)

    item = Item(use_function=castFire, value=(damage, radius, mrange))

    returnItem = Actor(x, y, "Fireball Scroll", "fireScroll", item=item,
                       depth=constant.itemDepth)

    return returnItem


def genConfusionScroll(coords):
    x, y = coords

    turns = tcod.random_get_int(0, 5, 10)

    item = Item(use_function=castConfusion, value=turns)

    returnItem = Actor(x, y, "Confusion Scroll", "confuseScroll", item=item,
                       depth=constant.itemDepth)

    return returnItem


def genHealth(coords):
    x, y = coords

    health = tcod.random_get_int(0, 3, 7)

    item = Item(use_function=castHeal, value=health)

    returnItem = Actor(x, y, "Carrot", "carrot", item=item,
                       depth=constant.itemDepth)

    return returnItem


def gameLoop():

    quit = False
    playerAct = "no-action"

    while not quit:

        playerAct = handleKeys()

        calculateMapFov()

        if playerAct == "QUIT":
            quitGame()

        for obj in game.currentObjects:
            if obj.ai:
                if playerAct != "no-action":
                    obj.ai.takeTurn()
            if obj.exitportal:
                obj.exitportal.update()

        if player.state == "DEAD" or player.state == "win":
            quit = True

        # draw
        draw()

        pygame.display.flip()
        clock.tick(constant.gameFPS)


def gameInt():
    global mainSurface, mapSurface, clock, calcFov, enemy, asset, camera, randomness, preferences

    pygame.init()
    pygame.key.set_repeat(200, 70)

    try:
        loadPreferences()
    except:
        preferences = Preferences()

    mainSurface = pygame.display.set_mode((constant.cameraWidth, constant.cameraHeight))

    mapSurface = pygame.Surface((constant.mapWidth * constant.cellWidth,
                                 constant.mapHeight * constant.cellHeight))

    camera = Camera()

    asset = Assets()

    clock = pygame.time.Clock()

    randomness = random.SystemRandom()

    calcFov = True


def newGame():
    global game

    game = GameObject()
    gen_player((0, 0))
    placeObjects(game.currentRooms)


def handleKeys():
    global calcFov
    # Get Input
    keyList = pygame.key.get_pressed()
    events = pygame.event.get()

    modKey = keyList[pygame.K_LSHIFT] or keyList[pygame.K_RSHIFT]

    # process
    for event in events:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.creature.move(0, -1)
                calcFov = True
                return "player-moved"

            if event.key == pygame.K_s:
                player.creature.move(0, 1)
                calcFov = True
                return "player-moved"

            if event.key == pygame.K_a:
                player.creature.move(-1, 0)
                calcFov = True
                return "player-moved"

            if event.key == pygame.K_d:
                player.creature.move(1, 0)
                calcFov = True
                return "player-moved"

            if event.key == pygame.K_e:
                objectsAtPlayer = objectsAtCoords(player.x, player.y)

                for obj in objectsAtPlayer:
                    if obj.item and not obj.stairs:
                        obj.item.pickUp(player)

            if event.key == pygame.K_SPACE:
                if len(player.container.inventory) > 0:
                    player.container.inventory[-1].item.drop(player.x, player.y)

            if event.key == pygame.K_ESCAPE:
                menuPause()

            if event.key == pygame.K_TAB:
                menuInventory()

            if event.key == pygame.K_UP:
                objList = objectsAtCoords(player.x, player.y)

                for obj in objList:
                    if obj.stairs:
                        obj.stairs.use()
                    if obj.exitportal:
                        obj.exitportal.use()

    return "no-action"


def gameMessage(msg, color = constant.colorGrey):
    game.messageHistory.append((msg, color))


def quitGame():

    saveGame()

    # and quit
    pygame.quit()
    exit()


def saveGame():

    for obj in game.currentObjects:
        obj.destroy()

    # Save and encrypt (because we are that concerned with people hacking their save data)
    # this also compresses files in case you have 100 maps or something
    with gzip.open('data\playerInfo\savedata', 'wb') as file:
        pickle.dump([game, player], file)


def loadGame():
    global game, player

    with gzip.open('data\playerInfo\savedata', 'rb') as file:
        game, player = pickle.load(file)

    for obj in game.currentObjects:
        obj.resurrect()

    makeMapFov(game.currentMap)


def savePreferences():
    with gzip.open('data\playerInfo\\userPrefs', 'wb') as file:
        pickle.dump(preferences, file)


def loadPreferences():
    global preferences

    with gzip.open('data\\userPrefs', 'rb') as file:
        preferences = pickle.load(file)


mainMenu()



