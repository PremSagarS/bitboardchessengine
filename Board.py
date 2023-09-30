from ChessFunctionsAndConstants import *


class Board:
    def __init__(self) -> None:
        # there are 23 bitboards though only 12 are needed.
        # this is because I want the index of the bitboard
        # to be the same as the integer representation of the piece

        self.board = [EMPTY] * 64
        self.bitboards = [uint64(0)] * 23
        self.castlingRights = []
        self.previousMoves = []
        self.halfMoveCounter = 0
        self.fullMoveCounter = 0
        self.currentTurn = 0
        self.enPassantSquare = None

        self.setToFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def printBoard(self) -> None:
        print("-" * 17)
        for i in range(64):
            if i % 8 == 0:
                print("|", end="")
            print(pieceToCharacter(self.board[i]) + "|", end="")
            if i % 8 == 7:
                print("")
                print("-" * 17)

    def setToFen(self, fen: str) -> None:
        # get info from FEN
        (
            position,
            toMove,
            castlingRights,
            enPassant,
            halfMoveCounter,
            fullMoveCounter,
        ) = fen.split(" ")

        # reset board
        self.board = [EMPTY] * 64

        # set board to fen
        index = 0
        for char in position:
            if char.isdigit():
                index += int(char)
            elif char == "/":
                continue
            else:
                self.board[index] = characterToPiece(char)
                index += 1

        if toMove == "w":
            self.currentTurn = WHITE
        else:
            self.currentTurn = BLACK

        self.castlingRights = [
            "K" in castlingRights,
            "Q" in castlingRights,
            "k" in castlingRights,
            "q" in castlingRights,
        ]

        if enPassant == "-":
            self.enPassantSquare = None
        else:
            self.enPassantSquare = squareNameToIndex(enPassant)

        self.halfMoveCounter = int(halfMoveCounter)

        self.fullMoveCounter = int(fullMoveCounter)

        self.updateBitBoards()

    def updateBitBoards(self) -> None:
        for squareIndex in range(64):
            piece = self.board[squareIndex]
            pieceBitBoard = self.bitboards[piece]
            self.bitboards[piece] = setBit(pieceBitBoard, squareIndex)

        black_bitboard = uint64(0)
        for i in range(BLACK | PAWN, BLACK | KING + 1):
            black_bitboard = black_bitboard | self.bitboards[i]
        self.bitboards[BLACK] = black_bitboard

        white_bitboard = uint64(0)
        for i in range(WHITE | PAWN, WHITE | KING + 1):
            white_bitboard = white_bitboard | self.bitboards[i]
        self.bitboards[WHITE] = white_bitboard
