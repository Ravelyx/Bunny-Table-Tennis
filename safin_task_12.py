import pygame
import sys, random

#Controls menus of game
def menu():
    global disallowClick

    pygame.mixer.music.load('./srcAudio/menuMusic.mp3')
    pygame.mixer.music.play(-1)

    while True:

        screen.fill(resetScreen)
        screen.blit(bkgroundImg,(0,0))

        #Draws labels to screen
        textWriter('Welcome to Bunny Table Tennis!', menuFont, screenHeight/2-220, screenWidth/2-300)
        textWriter('Player one movement controls: W and S', menuFontInstructions, screenHeight/2-250, screenWidth/2)
        textWriter('Player two movement controls: O and L', menuFontInstructions, screenHeight/2-250, screenWidth/2+30)
        textWriter('www.lunest.se', menuFontInstructions, screenHeight/2+315, screenWidth/2+100)

        #Tracks mouse cursor position
        x, y = pygame.mouse.get_pos()
 
        gameAI = singlePlayer.get_rect()
        gameAI.center = (150,screenWidth/2+160)
        game2P = multiPlayer.get_rect()
        game2P.center = (430, screenWidth/2+160)
        creditsButton = credits.get_rect()
        creditsButton.center = (680, screenWidth/2+160)

        #Checks mouse cursor position relative to collision point for buttons.
        if gameAI.collidepoint((x, y)):
            if disallowClick:
                game('AI')
        if game2P.collidepoint((x, y)):
            if disallowClick:
                game('2p')
        if creditsButton.collidepoint((x, y)):
            if disallowClick:
                creditsMenu()
        
        #Draws buttons to screen
        screen.blit(singlePlayer, gameAI)
        screen.blit(multiPlayer, game2P)
        screen.blit(credits, creditsButton)

        #Disallows click if True. Used to reallow clicks upon re-entering menu from game.
        disallowClick = False

        for event in pygame.event.get():
            
            #Window X button closes game.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            #Disallows clicks upon game entry in order to avoid unintended consequences.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    disallowClick = True

        pygame.display.update()
        clock.tick(60)

#Controls actual game
def game(mode):

    pygame.mixer.music.load('./srcAudio/noMonkey.wav')
    pygame.mixer.music.play(-1)

    #Delays the game at win/lose screen for texts to be readable.
    pauseDelay = True

    #Looots of global variables required because PyGame doesn't act as intended otherwise.
    global playerSpeed, AISpeed, playerPos, AIPos, ballPos, playerPoints, AIPoints

    #Controls ball movement and collision
    def ballMovement():
        global ballSpeedX, ballSpeedY, playerPoints, AIPoints, goalCollision, playerPos, AIPos

        ballPos.x += ballSpeedX
        ballPos.y += ballSpeedY

        #Bounces ball off walls
        if ballPos.top <= 0 or ballPos.bottom >= screenHeight:
            ballSpeedY *= -1

        if ballPos.left <= 0:
            scoreNoise.play()
            goalCollision = pygame.time.get_ticks()
            AIPoints += 1
            playerPos.center = (20, screenHeight / 2)
            AIPos.center = (screenWidth - 20, screenHeight / 2)

        if ballPos.right >= screenWidth:
            scoreNoise.play()
            goalCollision = pygame.time.get_ticks()
            playerPoints += 1
            playerPos.center = (20, screenHeight / 2)
            AIPos.center = (screenWidth - 20, screenHeight / 2)

        #Makes ball bounce off AI/Player 2.
        if ballPos.colliderect(AIPos) and ballSpeedX > 0:

            bounceNoise.play()

            if abs(ballPos.right - AIPos.left) < 10:
                ballSpeedX *= -1
            elif abs(ballPos.bottom - AIPos.top) < 10 and ballSpeedY > 0:
                ballSpeedY *= -1
            elif abs(ballPos.top - AIPos.bottom) < 10 and ballSpeedY < 0:
                ballSpeedY *= -1

        #Makes ball bounce off player
        if ballPos.colliderect(playerPos) and ballSpeedX < 0:

            bounceNoise.play()

            if abs(ballPos.left - playerPos.right) < 10:
                ballSpeedX *= -1
            elif abs(ballPos.bottom - playerPos.top) < 10 and ballSpeedY > 0:
                ballSpeedY *= -1
            elif abs(ballPos.top - playerPos.bottom) < 10 and ballSpeedY < 0:
                ballSpeedY *= -1

    #Restricts player movement & helps player move.
    def playerMovement():
        playerPos.y += playerSpeed

        if playerPos.top <= 0:
            playerPos.top = 0
        if playerPos.bottom >= screenHeight:
            playerPos.bottom = screenHeight

    #Restricts AI movement & helps AI move. Makes it follow ball as well.
    def AIMovement():
        AISpeed = 8
        if AIPos.top < ballPos.y:
            AIPos.y += AISpeed
        if AIPos.bottom > ballPos.y:
            AIPos.y -= AISpeed

        #Stop AI moving off screen
        if AIPos.top <= 0:
            AIPos.top = 0
        if AIPos.bottom >= screenHeight:
            AIPos.bottom = screenHeight

    #Restricts Player 2 movement & helps movement.
    def twoPlayerMovement():
        AIPos.y += AISpeed

        if AIPos.top <= 0:
            AIPos.top = 0
        if AIPos.bottom >= screenHeight:
            AIPos.bottom = screenHeight

    #Player 1 win screen.
    def winScreen():
        global playerPoints, AIPoints
        gameFont = pygame.font.SysFont(defaultFont, 40)
        if mode == "AI":
            screenText = gameFont.render('You won! Restarting match...', True, (0, 0, 0))
        else:
            screenText = gameFont.render('Player 1 won! Restarting match...', True, (0, 0, 0))
        screen.blit(screenText, (10, 10))
        pygame.display.update()
        pygame.time.delay(3000)
        AIPoints = 0
        playerPoints = 0

    #AI/Player 2 win screen
    def loseScreen():
        global playerPoints, AIPoints
        gameFont = pygame.font.SysFont(pygame.font.get_default_font(), 40)
        if mode == "AI":
            screenText = gameFont.render('You lost! Restarting match...', True, (0, 0, 0))
        else:
            screenText = gameFont.render('Player 2 won! Restarting match...', True, (0, 0, 0))
        screen.blit(screenText, (10, 10))
        pygame.display.update()
        pygame.time.delay(3000)
        AIPoints = 0
        playerPoints = 0

    #Makes ball move at start of each round & on score.
    def startBall():
        global ballSpeedX, ballSpeedY, goalCollision, playerPoints, AIPoints

        ballPos.center = (screenWidth / 2, screenHeight / 2)
        timeNow = pygame.time.get_ticks()

        # Stalls game for 1200 ticks
        if timeNow - goalCollision < 1200:
            ballSpeedY, ballSpeedX = 0, 0
        else:
            ballSpeedX = 6 * random.choice((-1, 1))
            ballSpeedY = 6 * random.choice((-1, 1))
            goalCollision = None

        if playerPoints == 3:
            winScreen()
        elif AIPoints == 3:
            loseScreen()

    #Controls whether game runs or not.
    runGame = True
    while runGame:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    playerSpeed -= 8
                if event.key == pygame.K_s:
                    playerSpeed += 8
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    playerSpeed += 8
                if event.key == pygame.K_s:
                    playerSpeed -= 8
                if event.key == pygame.K_ESCAPE:
                    AIPoints = 0
                    playerPoints = 0
                    ballPos.center = (screenWidth/2,screenHeight/2)
                    playerPos.center = playerPos.center = (20, screenHeight / 2)
                    AIPos.center = (screenWidth - 20, screenHeight / 2)
                    pygame.mixer.music.load('./srcAudio/menuMusic.mp3')
                    pygame.mixer.music.play(-1)
                    runGame = False

            if mode == "2p":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        AISpeed -= 8
                    if event.key == pygame.K_l:
                        AISpeed += 8
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_o:
                        AISpeed += 8
                    if event.key == pygame.K_l:
                        AISpeed -= 8

        #Load game funcs.
        ballMovement()
        playerMovement()

        if (mode == 'AI'):
            AIMovement()
        else:
            twoPlayerMovement()

        #Draw to screen
        screen.fill(resetScreen)
        for y in range(5):
            for x in range(6):
                screen.blit(arenaBG,(x*1,y*150))
                screen.blit(arenaBG,(x*545,y*200))
                screen.blit(midBG,(x*58,y*250))
                  
        screen.blit(AITable, AIPos)
        screen.blit(playerTable, playerPos)
        screen.blit(ballTable,ballPos)
        playerScoreText = scoreFont.render(f'{playerPoints}', True, black)
        screen.blit(playerScoreText, (200, 500))
        enemyScoreText = scoreFont.render(f'{AIPoints}', True, black)
        screen.blit(enemyScoreText, (600, 500))
        textWriter('Press ESC to quit', menuFontTiny, screenHeight/2+350, screenWidth/2+180)
        textWriter('Best of 3!', menuFontTiny, screenHeight/2+405, screenWidth/2-380)
        
        #Detects collision.
        if goalCollision:
            startBall()

        #Initial start delay (match start)
        if pauseDelay:
            pygame.display.update()
            pygame.time.delay(2000)
            pauseDelay = False

        pygame.display.flip()
        clock.tick(60)

#Credits where they're due
def creditsMenu():

    creditsScreen = True

    while creditsScreen:
        screen.fill(resetScreen)
        screen.blit(creditsBG,(10,40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    creditsScreen = False
        
        #Writes text. Forgot to put in colour-choice to textWriter function,
        #so had to implement this one manually for white colour. Too lazy to change this.
        ESCObjText = menuFontTiny.render('Press ESC to return', 1, white)
        ESCRect = ESCObjText.get_rect()
        ESCRect.topleft = (screenHeight/2+335,screenWidth/2+180)
        screen.blit(ESCObjText, ESCRect)

        pygame.display.update()
        clock.tick(60)

#Text writer to add labels in game
def textWriter(text, font, height, width):
    writeObject = font.render(text, True, black)
    rect = writeObject.get_rect()
    rect.topleft = (height, width)
    screen.blit(writeObject, rect)

# Game setup
pygame.init()
clock = pygame.time.Clock()

# Game screen settings & pygame init
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight), 0, 32)
pygame.display.set_caption("Bunny Table Tennis")
pygame.font.init()
pygame.display.set_icon(pygame.image.load('./srcImages/playerTable.png'))

# Colliders & Sprites
ballTable = pygame.image.load("./srcImages/ballTable.png")
ballPos = ballTable.get_rect()
ballPos.center = (screenWidth/2,screenHeight/2)

playerTable = pygame.image.load("./srcImages/playerTable.png")
playerPos = playerTable.get_rect()
playerPos.center = (20, screenHeight / 2)

AITable = pygame.image.load("./srcImages/enemyTable.png")
AIPos = AITable.get_rect()
AIPos.center = (screenWidth - 20, screenHeight / 2)

singlePlayer = pygame.image.load("./srcImages/singleplayer_button.png")
multiPlayer = pygame.image.load("./srcImages/2P.png")
credits = pygame.image.load("./srcImages/credits_button.png")
creditsBG = pygame.image.load("./srcImages/credits_BG.png").convert()
bkgroundImg = pygame.image.load("./srcImages/lvl_select_BG.png").convert()
arenaBG = pygame.image.load("./srcImages/SpringBGE.png").convert()
midBG = pygame.image.load("./srcImages/SpringBGM.png").convert()

# Variable settings
ballSpeedX = 5 * random.choice((-1, 1))
ballSpeedY = 5 * random.choice((-1, 1))
playerSpeed = 0
AISpeed = 0
AIPoints = 0
playerPoints = 0
goalCollision = True
disallowClick = False
scoreFont = pygame.font.Font(pygame.font.get_default_font(), 40)
defaultFont = pygame.font.get_default_font()
disallowClick = False
menuFont = pygame.font.SysFont(None, 60)
menuFontTiny = pygame.font.SysFont(None, 25)
menuFontInstructions = pygame.font.SysFont(None, 35)
pauseDelay = False
runGame = False
creditsScreen = False
white = (255, 255, 255)
black = (0,0,0)
resetScreen = pygame.Color('black')
bounceNoise = pygame.mixer.Sound('./srcAudio/bouncesound.wav')
scoreNoise = pygame.mixer.Sound('./srcAudio/scoreSound.wav')

#Runs the game
menu()
