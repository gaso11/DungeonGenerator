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
mapWidth = 100
mapHeight = 100
mapMaxNumRooms = 50

#Room
roomMaxHeight = 7
roomMinHeight = 3
roomMaxWidth = 7
roomMinWidth = 3

#Colors
colorBlack = (0, 0, 0)
colorWhite = (255, 255, 255)
colorGrey = (100, 100, 100)
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
debugFont = pygame.font.Font("data/joystix.ttf", 20)
messageTextFont = pygame.font.Font("data/joystix.ttf", 12)
cursorFont = pygame.font.Font("data/joystix.ttf", cellHeight)