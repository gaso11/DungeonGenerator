"""
Sorry I suck at commenting
Press ESC to pause (which isn't useful right now
Press TAB to open inventory
Press Shift to open Tile Select
Press SPACE to drop last grabbed item
"""


import pygame
import tcod
import constant


class Tile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False


class Assets:
    def __init__(self):
        # Sheets
        self.Sheet = SpriteSheet("data/reptileSheet.png")
        self.Sheet2 = SpriteSheet("data/aquaticSheet.png")

        # Animations
        self.player = self.Sheet.getAnimation('o', 5, 16, 16, 2, (32, 32))
        self.enemy = self.Sheet2.getAnimation('k', 1, 16, 16, 2, (32, 32))

        # Sprites
        self.wall = pygame.image.load("data/wall2.jpg")
        self.wallSeen = pygame.image.load("data/wallunseen2.png")
        self.floor = pygame.image.load("data/floor.jpg")
        self.floorSeen = pygame.image.load("data/floorunseen2.png")


class Actor:
    def __init__(self, x, y, name, animation, animateSpeed=.5,
                 creature=None, ai=None, container=None, item=None):
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

    def draw(self):
        isVisible = tcod.map_is_in_fov(mapFov, self.x, self.y)

        if isVisible:
            if len(self.animation) == 1:
                mainSurface.blit(self.animation[0], (self.x * constant.cellWidth, self.y * constant.cellHeight))
            elif len(self.animation) > 1:
                if clock.get_fps() > 0.0:
                    self.flickerTimer += 1 / clock.get_fps()

                if self.flickerTimer >= self.flickerSpeed:
                    self.flickerTimer = 0.0

                    if self.spriteImage >= len(self.animation) - 1:
                        self.spriteImage = 0
                    else:
                        self.spriteImage += 1
                mainSurface.blit(self.animation[self.spriteImage],
                                 (self.x * constant.cellWidth, self.y * constant.cellHeight))


class GameObject:
    def __init__(self):
        self.currentMap = createMap()
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


class Creature:
    def __init__(self, name, hp=10, deathFunction = None):
        self.name = name
        self.maxHp = hp
        self.hp = hp
        self.deathFunction = deathFunction

    def move(self, dx, dy):

        tileIsWall = (game.currentMap[self.owner.x + dx][self.owner.y + dy].blockPath == True)

        target = checkMapForCreatures(self.owner.x + dx, self.owner.y + dy, self.owner)

        if target:
            self.attack(target, 5)

        if not tileIsWall and target is None:
            self.owner.x += dx
            self.owner.y += dy

    def attack(self, target, damage):
        gameMessage(self.name + " attacks " + target.creature.name + " for " + str(damage) + " damage!", constant.colorWhite)

        target.creature.takeDamage(5)

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
        if self.use_function:
            result = self.use_function(self.container.owner, self.value)

            if result is not None:
                pass

            else:
                self.container.inventory.remove(self.owner)


class Container:
    def __init__(self, volume = 10.0, inventory = []):
        self.inventory = inventory
        self.maxVol = volume

    @property
    def volume(self):
        return 0.0


class AITest:
    # Pretty dumb AI

    def takeTurn(self):
        self.owner.creature.move(tcod.random_get_int(None, -1, 1), tcod.random_get_int(None, -1, 1))


def deathMonster(monster):
    gameMessage(monster.creature.name + " is dead!", constant.colorGrey)

    monster.creature = None
    monster.ai = None


def createMap():
    map = [[Tile(False) for y in range(0, constant.mapHeight)] for x in range(0, constant.mapWidth)]

    map[10][10].blockPath = True
    map[10][15].blockPath = True

    for x in range(constant.mapWidth):
        map[x][0].blockPath = True
        map[x][constant.mapHeight - 1].blockPath = True

    for y in range(constant.mapHeight):
        map[0][y].blockPath = True
        map[constant.mapWidth - 1][y].blockPath = True

    makeMapFov(map)

    return map


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




def drawMap(toDraw):
    for x in range(0, constant.mapWidth):
        for y in range(0, constant.mapHeight):

            isVisible = tcod.map_is_in_fov(mapFov, x, y)

            if isVisible:

                toDraw[x][y].explored = True

                if toDraw[x][y].blockPath == True:
                    # wall
                    mainSurface.blit(asset.wall, (x * constant.cellWidth, y * constant.cellHeight))
                else:
                    # floor
                    mainSurface.blit(asset.floor, (x * constant.cellWidth, y * constant.cellHeight))

            elif toDraw[x][y].explored:
                if toDraw[x][y].blockPath == True:
                    # wall
                    mainSurface.blit(asset.wallSeen, (x * constant.cellWidth, y * constant.cellHeight))
                else:
                    # floor
                     mainSurface.blit(asset.floorSeen, (x * constant.cellWidth, y * constant.cellHeight))


def draw():
    global mainSurface

    # clear
    mainSurface.fill(constant.colorDefaultBG)

    # map
    drawMap(game.currentMap)

    # character
    for obj in game.currentObjects:
        obj.draw()

    drawDebug()
    drawMessages()

    # update


def drawDebug():
    drawText(mainSurface, "fps: " + str(int(clock.get_fps())), constant.debugFont, (0, 0),
             constant.colorWhite, constant.colorBlack)


def drawMessages():
    if len(game.messageHistory) <= constant.numMessages:
        toDraw = game.messageHistory
    else:
        toDraw = game.messageHistory[-constant.numMessages:]

    textHeight = helperTextHeight(constant.messageTextFont)

    startY = (constant.mapHeight * constant.cellHeight - (constant.numMessages * textHeight)) - 5

    i = 0

    for message, color in toDraw:

        drawText(mainSurface, message, constant.messageTextFont, (0, startY + (i * textHeight)),
                 color, constant.colorBlack)

        i += 1


def drawTileRect(coords):

    x, y = coords

    x = x * constant.cellWidth
    y = y * constant.cellHeight

    selSurface = pygame.Surface((constant.cellWidth, constant.cellHeight))
    selSurface.fill(constant.colorWhite)
    selSurface.set_alpha(150)
    mainSurface.blit(selSurface, (x, y))


def drawText(surface, text, font, coord, color, background = None):
    textSurf, textRect = helperTextObj(text, font, color, background)

    textRect.topleft = coord

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


def castLightning(damage):
    point = menuSelectTarget(origin=(player.x, player.y), range=5, penWall=False)

    if point:
        tileList = findLine((player.x, player.y), point)

        for i, (x, y) in enumerate(tileList):
            target = checkMapForCreatures(x, y)

            if target:
                target.creature.takeDamage(damage)

def menuPause():
    isClosed = False

    windowWidth = constant.mapWidth * constant.cellWidth
    windowHeight = constant.mapHeight * constant.cellHeight

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
    windowWidth = constant.mapWidth * constant.cellWidth
    windowHeight = constant.mapHeight * constant.cellHeight
    menuX = (windowWidth / 2) - (menuWidth / 2)
    menuY = (windowHeight / 2) - (menuHeight / 2)
    menuFont = constant.messageTextFont
    menuTextHeight = helperTextHeight(menuFont)
    color = constant.colorWhite

    invSurface = pygame.Surface((menuWidth, menuHeight))

    while not isClosed:

        invSurface.fill(constant.colorBlack)

        printList = [obj.name for obj in player.container.inventory]

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

        mainSurface.blit(invSurface, (menuX, menuY))

        clock.tick(constant.gameFPS)

        pygame.display.update()


def menuSelectTarget(origin=None, range=None, penWall= True):
    isClosed = False

    while not isClosed:
        mouseX, mouseY = pygame.mouse.get_pos()
        eventList = pygame.event.get()

        mapX = int(mouseX / constant.cellWidth)
        mapY = int(mouseY / constant.cellHeight)

        validTiles = []

        if origin:
            tileList = findLine(origin, (mapX, mapY))

            for i, (x, y) in enumerate(tileList):

                validTiles.append((x, y))

                if range and i == range - 1:
                    break

                if not penWall and game.currentMap[x][y].blockPath:
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

        draw()

        for (tileX, tileY) in validTiles:
            drawTileRect((tileX, tileY))

        pygame.display.flip()

        clock.tick(constant.gameFPS)


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
    global mainSurface, game, clock, calcFov, player, enemy, asset

    pygame.init()
    pygame.key.set_repeat(200, 70)

    mainSurface = pygame.display.set_mode((constant.mapWidth * constant.cellWidth,
                                           constant.mapHeight * constant.cellHeight))

    game = GameObject()

    clock = pygame.time.Clock()

    calcFov = True

    asset = Assets()

    container1 = Container()
    creature1 = Creature("Greg")
    player = Actor(1, 1, "python", asset.player, animateSpeed=1, creature=creature1,
                   container=container1)

    item1 = Item(value = 5, use_function=castHeal)
    creature2 = Creature("Jackie", deathFunction=deathMonster)
    ai1 = AITest()
    enemy = Actor(15, 15, "smart crab", asset.enemy, animateSpeed=1, creature=creature2, ai=ai1,
                  item=item1)

    item2 = Item(value = 4, use_function=castHeal)
    creature3 = Creature("Bob", deathFunction=deathMonster)
    ai2 = AITest()
    enemy2 = Actor(15, 15, "dumb crab", asset.enemy, animateSpeed=1, creature=creature3, ai=ai2,
                  item=item2)

    game.currentObjects = [player, enemy, enemy2]


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

            if event.key == pygame.K_LSHIFT:
                castLightning(10)

    return "no-action"


def gameMessage(msg, color = constant.colorGrey):
    game.messageHistory.append((msg, color))


gameInt()
gameLoop()



