import pygame

pygame.init()

#Game Size
gameWidth = 800
gameHeight = 600
cellWidth = 32  # tiles are all 32pixels
cellHeight = 32

#FPS
gameFPS = 60

#Map
mapWidth = 20
mapHeight = 20

#Colors
colorBlack = (0, 0, 0)
colorWhite = (255, 255, 255)
colorGrey = (100, 100, 100)
colorRed = (255, 0, 0)

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