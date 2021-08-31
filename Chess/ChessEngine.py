'''
This class is responsible for storing information of about the current state of chess game.
It will also responsible for determining valid moves at current state and keep a move log
'''
import numpy


class GameState:
    def __init__(self, is_black):
        # board is an 8x8 2 dimensional list, each element in list contain 2 characters
        # first character represent color of piece
        # second character represent type of piece
        # '--' is a blank position
        self.board = numpy.array([
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ])
        self.WhiteToMove = True
        self.move_log = []
        self.move_function = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'K': self.getKingMoves,
                              'N': self.getKnightMoves, 'Q': self.getQueenMoves, 'B': self.getBishopMoves}
        self.WhiteKingpos = (7, 4)
        self.BlackKingpos = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # square where en passant captured is possible\
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRight(True, True, True, True)
        self.Castlinglog = [
            CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                        self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.move_log.append(move)
        self.WhiteToMove = not self.WhiteToMove
        # update king location if undo move
        if move.pieceMoved == 'wk':
            self.WhiteKingpos = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bk':
            self.BlackKingpos = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # en passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle moves
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'

            else:  # queen side move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)
        # update castle rights whenever it is a king or rook move
        self.updateCastleRights(move)
        self.Castlinglog.append(
            CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                        self.currentCastlingRight.bqs))

    '''
    Undo last move 
    '''

    def undoMove(self):
        if len(self.move_log) != 0:  # make sure there is a move to undo
            last_move = self.move_log.pop()
            self.board[last_move.startRow][last_move.startCol] = last_move.pieceMoved
            self.board[last_move.endRow][last_move.endCol] = last_move.pieceCaptured
            self.WhiteToMove = not self.WhiteToMove  # switch turn
            # update king location if moved
            if last_move.pieceMoved == 'wk':
                self.WhiteKingpos = (last_move.startRow, last_move.startCol)
            elif last_move.pieceMoved == 'bk':
                self.BlackKingpos = (last_move.startRow, last_move.startCol)

            # undo en passant
            if last_move.isEnPassantMove:
                self.board[last_move.endRow][last_move.endCol] = '--'
                self.board[last_move.startRow][last_move.endCol] = last_move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo castle right
            self.Castlinglog.pop()
            self.currentCastlingRight = self.Castlinglog[-1]

            # undo castle move
            if last_move.isCastleMove:
                if last_move.endCol - last_move.startCol == 2:  # king side move
                    self.board[last_move.endRow][last_move.endCol + 1] = self.board[last_move.endRow][
                        last_move.endCol - 1]
                    self.board[last_move.endRow][last_move.endCol - 1] = '--'

                else:  # queen side move
                    self.board[last_move.endRow][last_move.endCol - 2] = self.board[last_move.endRow][
                        last_move.endCol + 1]
                    self.board[last_move.endRow][last_move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    '''
    Update current castle rights given a move
    '''

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wk':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bk':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False

        # if piece captured is rook

        elif move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:  # right rook
                    self.currentCastlingRight.wks = False

    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRight(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                         self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.WhiteToMove:
            king_row = self.WhiteKingpos[0]
            king_col = self.WhiteKingpos[1]
        else:
            king_row = self.BlackKingpos[0]
            king_col = self.BlackKingpos[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow,
                                moves[i].endCol) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.WhiteToMove:
                self.getCastleMoves(self.WhiteKingpos[0], self.BlackKingpos[1], moves)
            else:
                self.getCastleMoves(self.BlackKingpos[0], self.BlackKingpos[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                # TODO stalemate on repeated moves
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.currentCastlingRight = temp_castle_rights
        return moves

    '''
    Return if player is in check, a list of pins, a list of checks
    '''

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.WhiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.WhiteKingpos[0]
            start_col = self.WhiteKingpos[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.BlackKingpos[0]
            start_col = self.BlackKingpos[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    '''
    Determine if current player in check
    '''

    def inCheck(self):
        if self.WhiteToMove:
            return self.squareUnderAttack(self.WhiteKingpos[0], self.WhiteKingpos[1])
        else:
            return self.squareUnderAttack(self.BlackKingpos[0], self.BlackKingpos[1])

    '''
    Determine if the enemy can attack piece at r, c
    '''

    def squareUnderAttack(self, r, c):
        self.WhiteToMove = not self.WhiteToMove  # switch turn
        oppMoves = self.getAllPossibleMoves()
        self.WhiteToMove = not self.WhiteToMove  # switch turn back

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True

        return False

    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[row][col][1]
                    self.move_function[piece](row, col, moves)
        return moves

    '''
    Get all pawn moves for the pawn located at row, col and add these to list 
    '''

    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.WhiteToMove:  # White pawns moves
            kingRow, kingCol = self.WhiteKingpos
            if self.board[r - 1][c] == '--':
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == '--':
                        moves.append(Move((r, c), (r - 2, c), self.board))

            if c > 0:  # Capture left
                if not piece_pinned or pin_direction == (-1, -1):
                    if self.board[r - 1][c - 1][0] == 'b':

                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enpassantPossible:
                        attackingPiece = blockingPiece = False
                        if kingRow == r:
                            if kingCol < c:  # king is left of the pawn
                                # inside range between king and pawn, outside range between pawn and border
                                insideRange = range(kingCol + 1, c - 1)
                                outsideRange = range(c + 1, 8)
                            else:  # king is right of the pawn
                                insideRange = range(kingCol - 1, c, -1)
                                outsideRange = range(c - 2, -1, -1)

                            for i in insideRange:
                                if self.board[r][i] != '--':  # some other piece between en passant piece block
                                    blockingPiece = True

                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == 'b' and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockingPiece = True

                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r - 1, c - 1), self.board, True))
            if c < 7:  # Capture right
                if not piece_pinned or pin_direction == (-1, 1):
                    if self.board[r - 1][c + 1][0] == 'b':

                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enpassantPossible:
                        attackingPiece = blockingPiece = False
                        if kingRow == r:
                            if kingCol < c:  # king is left of the pawn
                                # inside range between king and pawn, outside range between pawn and border
                                insideRange = range(kingCol + 1, c)
                                outsideRange = range(c + 2, 8)
                            else:  # king is right of the pawn
                                insideRange = range(kingCol - 1, c + 1, -1)
                                outsideRange = range(c - 1, -1, -1)

                            for i in insideRange:
                                if self.board[r][i] != '--':  # some other piece between en passant piece block
                                    blockingPiece = True

                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == 'b' and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockingPiece = True

                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r - 1, c + 1), self.board, True))

        else:  # black pawns moves
            kingRow, kingCol = self.BlackKingpos
            if self.board[r + 1][c] == '--':
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if c > 0:  # Capture left
                if not piece_pinned or pin_direction == (1, -1):
                    if self.board[r + 1][c - 1][0] == 'w':

                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enpassantPossible:
                        attackingPiece = blockingPiece = False
                        if kingRow == r:
                            if kingCol < c:  # king is left of the pawn
                                # inside range between king and pawn, outside range between pawn and border
                                insideRange = range(kingCol + 1, c - 1)
                                outsideRange = range(c + 1, 8)
                            else:  # king is right of the pawn
                                insideRange = range(kingCol - 1, c, -1)
                                outsideRange = range(c - 2, -1, -1)

                            for i in insideRange:
                                if self.board[r][i] != '--':  # some other piece between en passant piece block
                                    blockingPiece = True

                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == 'w' and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockingPiece = True

                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r + 1, c - 1), self.board, True))
            if c < 7:  # Capture right
                if not piece_pinned or pin_direction == (1, 1):
                    if self.board[r + 1][c + 1][0] == 'w':

                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enpassantPossible:
                        attackingPiece = blockingPiece = False
                        if kingRow == r:
                            if kingCol < c:  # king is left of the pawn
                                # inside range between king and pawn, outside range between pawn and border
                                insideRange = range(kingCol + 1, c)
                                outsideRange = range(c + 2, 8)
                            else:  # king is right of the pawn
                                insideRange = range(kingCol - 1, c + 1, -1)
                                outsideRange = range(c - 1, -1, -1)

                            for i in insideRange:
                                if self.board[r][i] != '--':  # some other piece between en passant piece block
                                    blockingPiece = True

                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == 'w' and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockingPiece = True

                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r + 1, c + 1), self.board, True))

    '''
            Get all rook moves for the rook located at row, col and add these to list 
    '''

    def getRookMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))  # right, left, down, up
        enemy_color = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # in board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:  # off board
                    break

    '''
        Get all knight moves for the knight located at row, col and add these to list 
    '''

    def getKnightMoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, 1), (-2, -1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, 2), (-1, -2))
        ally_color = 'w' if self.WhiteToMove else 'b'
        for m in knight_moves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # in board
                if not piece_pinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ally_color:  # empty space and enemy space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
            Get all king moves for the king located at row, col and add these to list 
    '''

    def getKingMoves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.WhiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.WhiteKingpos = (end_row, end_col)
                    else:
                        self.BlackKingpos = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.WhiteKingpos = (row, col)
                    else:
                        self.BlackKingpos = (row, col)

    '''
    Generate all valid castle moves of king at row, col and add them to list of moves 
    '''

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.WhiteToMove and self.currentCastlingRight.wks) or (
                not self.WhiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if (self.WhiteToMove and self.currentCastlingRight.wqs) or (
                not self.WhiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(row, col, moves)

    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, castle_move=True))

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, castle_move=True))

    '''
            Get all queen moves for the queen located at row, col and add these to list 
        '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
        Get all bishop moves for the bishop located at row, col and add these to list 
    '''

    def getBishopMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # 4 diagonals
        enemy_color = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # in board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:  # off board
                    break


class Move():
    # map keys to values

    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colstoFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSQ, endSQ, board, enpassant_move=False, castle_move=False):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnPassantMove = enpassant_move
        self.isCastleMove = castle_move
        self.is_capture = self.pieceCaptured != "--"
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding equal method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colstoFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        end_square = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.is_capture:
                return self.colstoFiles[self.startCol] + "x" + end_square
            else:
                return end_square + "Q" if self.isPawnPromotion else end_square

        move_string = self.pieceMoved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square


class CastleRight:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
