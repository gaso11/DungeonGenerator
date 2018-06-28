import pygame
import tcod
import constant
import math


class Tile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False


class Assets:
    def __init__(self):
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

        # Animations
        self.player = self.players.getAnimation('m', 4, 16, 16, 2, (32, 32))
        self.snake1 = self.enemies.getAnimation('a', 5, 16, 16, 4, (32, 32))
        self.snake2 = self.enemies.getAnimation('k', 5, 16, 16, 2, (32, 32))
        self.playerGhost = self.undead.getAnimation('e', 5, 16, 16, 2, (32, 32))

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

        tcod.namegen_parse("data/namegen/jice_celtic.cfg")


class Actor:
    def __init__(self, x, y, name, animation, animateSpeed=.5,
                 creature=None, ai=None, container=None, item=None, equipment=None):
        self.x = x
        self.y = y
        self.name = name
        self.animation = animation
        self.animateSpeed = animateSpeed / 1.0  # It demands a float

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


class GameObject:
    def __init__(self):
        self.currentObjects = []
        self.messageHistory = []


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
    def __init__(self, name, baseAttack=2, baseDefense=0, hp=10, deathFunction = None):
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
            deathPlayer()

    def takeDamage(self, damage):
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
    def __init__(self, weight = 0.0, volume = 0.0, use_function = None, value = None):
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
                game.currentObjects.remove(self.owner)
                self.container = actor.container

    def drop(self, x, y):
        game.currentObjects.append(self.owner)
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


class Container:
    def __init__(self, volume = 10.0, inventory = []):
        self.inventory = inventory
        self.maxVol = volume

    @property
    def volume(self):
        return 0.0

    @property
    def equippedItems(self):

        equippedList = [obj for obj in self.inventory
                        if obj.equipment and obj.equipment.equipped]

        return equippedList

def deathPlayer():
    gameMessage("you have died!", constant.colorGrey)

    player.animation = asset.playerGhost
#    monster.creature = None
#    monster.ai = None


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


def deathSnake(monster):
    gameMessage(monster.creature.name + " is dead!", constant.colorGrey)

    monster.animation = asset.deadSnake
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

            if len(list_of_rooms) == 0:
                gen_player(current_center)

            else:
                previous_center = list_of_rooms[-1].center

                map_create_tunnels(current_center, previous_center, new_map)

            list_of_rooms.append(new_room)

    makeMapFov(new_map)

    return new_map, list_of_rooms


def placeObjects(roomList):

    for room in roomList:
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
    for obj in game.currentObjects:
        obj.draw()

    mainSurface.blit(mapSurface, (0, 0), camera.rectangle)

    drawDebug()
    drawMessages()


def drawDebug():
#    drawText(mainSurface, "fps: "    + str(int(clock.get_fps())),   constant.debugFont, (0, 0),
     drawText(mainSurface, "health: " + str(int(player.creature.hp)), constant.debugFont, (constant.cameraWidth-180, constant.cameraHeight-30),
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

    container = Container()
    creature = Creature("Evan", baseAttack=4)
    player = Actor(x, y, "python", asset.player, animateSpeed=1, creature=creature,
                   container=container)

    game.currentObjects.append(player)


def genItem(coords):

    rand = tcod.random_get_int(0, 1, 5)

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
    else:
        print("Item creation failed")
        return

    game.currentObjects.append(item)


def genSword(coords):

    x, y = coords

    bonus = tcod.random_get_int(0, 1, 2)

    equipment = Equipment(attackBonus=bonus, slot="rightHand")

    returnItem = Actor(x, y, "Sword", asset.sword, equipment=equipment)

    return returnItem


def genShield(coords):
    x, y = coords

    bonus = tcod.random_get_int(0, 1, 2)

    equipment = Equipment(defenseBonus=bonus, slot="leftHand")

    returnItem = Actor(x, y, "Shield", asset.shield, equipment=equipment)

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
    snake = Actor(x, y, "Basic Snake", asset.snake1,
                  animateSpeed=1, creature=creature, ai=ai1)

    # game.currentObjects.append(basicSnake)
    return snake


def genSnakeHard(coords):
    x, y = coords

    health = tcod.random_get_int(0, 15, 20)
    attack = tcod.random_get_int(0, 3, 6)
    name = tcod.namegen_generate("Celtic male")

    creature = Creature(name, deathFunction=deathSnake, hp=health, baseAttack=attack)
    ai1 = AIChase()
    snake = Actor(x, y, "Hard Snake", asset.snake2,
                  animateSpeed=1, creature=creature, ai=ai1)

    # game.currentObjects.append(basicSnake)
    return snake


def genLightningScroll(coords):
    x, y = coords

    damage = tcod.random_get_int(0, 5, 7)
    mrange = tcod.random_get_int(0, 7, 8)

    item = Item(use_function=castLightning, value=(damage, mrange))

    returnItem = Actor(x, y, "Lightning Scroll", asset.lightScroll, item=item)

    return returnItem


def genFireballScroll(coords):
    x, y = coords

    damage = tcod.random_get_int(0, 2, 4)
    radius = 1
    mrange = tcod.random_get_int(0, 9, 12)

    item = Item(use_function=castFire, value=(damage, radius, mrange))

    returnItem = Actor(x, y, "Fireball Scroll", asset.fireScroll, item=item)

    return returnItem


def genConfusionScroll(coords):
    x, y = coords

    turns = tcod.random_get_int(0, 5, 10)

    item = Item(use_function=castConfusion, value=turns)

    returnItem = Actor(x, y, "Confusion Scroll", asset.confuseScroll, item=item)

    return returnItem


def gameLoop():
    quit = False
    playerAct = "no-action"

    while not quit:

        playerAct = handleKeys()

        calculateMapFov()

        if playerAct == "QUIT":
            quit = True

        elif playerAct != "no-action":
            for obj in game.currentObjects:
                if obj.ai:
                    obj.ai.takeTurn()

        # draw
        draw()

        pygame.display.flip()
        clock.tick(constant.gameFPS)

    # Loop is done
    pygame.quit()
    exit()


def gameInt():
    global mainSurface, mapSurface, game, clock, calcFov, enemy, asset, camera

    pygame.init()
    pygame.key.set_repeat(200, 70)

    mainSurface = pygame.display.set_mode((constant.cameraWidth, constant.cameraHeight))

    mapSurface = pygame.Surface((constant.mapWidth * constant.cellWidth,
                                 constant.mapHeight * constant.cellHeight))

    camera = Camera()

    asset = Assets()

    game = GameObject()
    game.currentMap, game.currentRooms = createMap()
    placeObjects(game.currentRooms)

    clock = pygame.time.Clock()

    calcFov = True


def handleKeys():
    global calcFov
    # Get Input
    events = pygame.event.get()

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
                    if obj.item:
                        obj.item.pickUp(player)

            if event.key == pygame.K_SPACE:
                if len(player.container.inventory) > 0:
                    player.container.inventory[-1].item.drop(player.x, player.y)

            if event.key == pygame.K_ESCAPE:
                menuPause()

            if event.key == pygame.K_TAB:
                menuInventory()

    return "no-action"


def gameMessage(msg, color = constant.colorGrey):
    game.messageHistory.append((msg, color))


gameInt()
gameLoop()



