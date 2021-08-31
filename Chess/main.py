'''
This is our main driver file. it will be responsible for handling user input and displaying current GameState
'''
import sys
from multiprocessing import Queue, Process

import pygame

from AI import findBestMove
from ChessEngine import GameState, Move

pygame.init()
WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
FPS = 120
IMAGES = {}

pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

FONT_BOLD = 'chess/assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'chess/assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'chess/assets/fonts/OpenSans-Light.ttf'
MENU_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * HEIGHT))
LARGE_TEXT = pygame.font.Font(FONT_REG, int(40 / 1080 * HEIGHT))
MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * HEIGHT))
SMALL_TEXT = pygame.font.Font(FONT_BOLD, 12)
HUD_TEXT = pygame.font.Font(FONT_REG, int(40 / 1440 * HEIGHT))

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 30
button_x_start = (WIDTH - BUTTON_WIDTH) // 2

button_layout_4 = [(button_x_start, HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                   (button_x_start, HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                   (button_x_start, HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                   (button_x_start, HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),]


def load_images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load('chess/images/' + piece + '.png'),
                                               (SQUARE_SIZE, SQUARE_SIZE))


def draw_window(screen, gs, valid_moves, sqSelected, ):
    draw_squares(screen)
    highlightSquares(screen, gs, valid_moves, sqSelected)
    draw_pieces(screen, gs.board)


'''
    Draw move log
'''

'''
def drawMoveLog(screen, gs, font):
    pygame.draw.rect(screen, pygame.Color('black'), (WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT))
    move_log = gs.move_log
    moveTexts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + ' '
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + ' '
        moveTexts.append(move_string)
    padding = 5
    text_y = padding
    line_spacing = 2
    movePerRow = 3
    for i in range(0,len(moveTexts), movePerRow):
        text = ''
        for j in range(movePerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        label = font.render(text, True, pygame.Color('white'))
        screen.blit(label, (WIDTH + padding, text_y))
        text_y += label.get_height() + line_spacing
'''


def draw_squares(screen):
    global colors
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


'''
    Highlight square selected and moves of piece selected
'''


def highlightSquares(screen, gs, valid_moves, sqSelected):
    if (len(gs.move_log)) > 0:
        last_move = gs.move_log[-1]
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color('green'))
        screen.blit(s, (last_move.endCol * SQUARE_SIZE, last_move.endRow * SQUARE_SIZE))
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.WhiteToMove else 'b'):  # sqSelected is a piece can move
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # set transparent
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))


'''
Animate piece move
'''


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        draw_squares(screen)
        draw_pieces(screen, board)
        # erased piece moved from it ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, color, endSquare)
        # draw captured piece onto piece
        if move.pieceCaptured != '--':
            if move.isEnPassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = pygame.Rect(move.endCol * SQUARE_SIZE, enPassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)


def draw_endgame_text(screen, text):
    font = pygame.font.SysFont('montserrat', 30)
    label = font.render(text, True, pygame.Color('gray'))
    screen.blit(label, (WIDTH / 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2))
    label = font.render(text, True, pygame.Color('black'))
    screen.blit(label, (WIDTH / 2 - label.get_width() // 2 + 2, HEIGHT // 2 - label.get_height() // 2 + 2))


def main(player1=True, player2=False):
    gs = GameState(True)
    load_images()
    run = True
    animate = False
    sqSelected = ()  # Keep track last click of player (tuple:(row,col))
    playerClicks = []  # Track of player click, element
    valid_moves = gs.getValidMoves()
    moveMade = False
    gameOver = False
    player1 = player1  # If a human playing white then this will be true vice_versa with Ai
    player2 = player2  # same as above but for black
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    while run:
        human_turn = (gs.WhiteToMove and player1) or (not gs.WhiteToMove and player2)
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # key handler
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == pygame.K_r:
                    gs = GameState()
                    valid_moves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == pygame.K_m:
                    main_menu()


            # mouse handler
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                    if sqSelected == (row, col) or col >= 8:  # user clicked same square twice or move log panel
                        sqSelected = ()  # Deselect
                        playerClicks = []  # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2 and human_turn:  # After second clicks
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.makeMove(valid_moves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # Deselect
                                playerClicks = []  # Clear player clicks
                        if not moveMade:
                            playerClicks = [sqSelected]

        # AI move finder
        if not gameOver and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=findBestMove, args=(gs, valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                gs.makeMove(ai_move)
                moveMade = True
                animate = True
                ai_thinking = False
        if moveMade:
            if animate:
                animateMove(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            moveMade = False
            animate = False
            move_undone = False
        draw_window(screen, gs, valid_moves, sqSelected)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            draw_endgame_text(screen, 'StaleMate' if gs.staleMate else 'Black wins' if gs.WhiteToMove else 'White wins')

        pygame.display.flip()


def button(text, x, y, w, h, click, inactive_colour=(33, 150, 243), active_colour=(0, 191, 255),
           text_colour=pygame.Color('white')):
    mouse = pygame.mouse.get_pos()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(screen, active_colour, (x, y, w, h))
        if click and pygame.time.get_ticks() > 100: return_value = True
    else:
        pygame.draw.rect(screen, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, colour=text_colour)
    text_rect.center = (int(x + w / 2), int(y + h / 2))
    screen.blit(text_surf, text_rect)
    return return_value


def text_objects(text, font, colour=pygame.Color('black')):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def main_menu_setup():
    screen.fill(pygame.Color('white'))
    text_surf, text_rect = text_objects('Chess 2.0', MENU_TEXT)
    text_rect.center = (int(WIDTH / 2), int(HEIGHT / 4))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects('v2.0', SMALL_TEXT)
    text_rect.center = (int(WIDTH * 0.96), int(HEIGHT * 0.96))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects('Created by Andrew Santos', LARGE_TEXT)
    text_rect.center = (int(WIDTH / 2), int(HEIGHT * 0.84))
    screen.blit(text_surf, text_rect)
    pygame.display.update()


def show_mouse():
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(True)


def main_menu():
    global gs
    show_mouse()
    main_menu_setup()
    start_game = False
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == pygame.KEYDOWN and (event.key == pygame.K_F4
                                                        and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])
                                                        or event.key == pygame.K_q or event.key == pygame.K_ESCAPE))
            if event.type == pygame.QUIT or alt_f4:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                main()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        if button('1 PLAYER', *button_layout_4[0], click):
            main()
        elif button('2 PLAYER', *button_layout_4[1], click):
            main(True, True)

        elif button('QUIT GAME', *button_layout_4[2], click):
            sys.exit()

        pygame.display.update(button_layout_4)
        clock.tick(120)


if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    main_menu()
