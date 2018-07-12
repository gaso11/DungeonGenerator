import pygame

pygame.init()

#Game Size
cameraWidth = 800
cameraHeight = 600
cellWidth = 32  # tiles are all 32pixels
cellHeight = 32

#FPS
gameFPS = 60
cameraSpeed = .10

#Map
mapWidth = 45
mapHeight = 45
mapMaxNumRooms = 15
mapLevels = 3

#Room
roomMaxHeight = 7
roomMinHeight = 3
roomMaxWidth = 7
roomMinWidth = 3

#Colors
colorBlack = (0, 0, 0)
colorWhite = (255, 255, 255)
colorGrey = (100, 100, 100)
colorDGrey = (50, 50, 50)
colorDDGrey = (25, 25, 25)
colorRed = (255, 0, 0)
colorGreen = (0, 255, 0)
colorBlue = (0, 0, 255)

#Game Colors
colorDefaultBG = colorGrey

#FOV settings
algoFov = 0
lightWalls = True
radius = 10

#Message Defaults
numMessages = 4

# Fonts
titleFont = pygame.font.Font("data/joystix.ttf", 26)
debugFont = pygame.font.Font("data/joystix.ttf", 20)
messageTextFont = pygame.font.Font("data/joystix.ttf", 12)
cursorFont = pygame.font.Font("data/joystix.ttf", cellHeight)

# Depth
playerDepth = -100
creatureDepth = 1
itemDepth = 2
corpseDepth = 100
backgroundDepth = 150