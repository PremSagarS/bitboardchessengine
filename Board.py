from ChessFunctionsAndConstants import *
from PreComputedTables import PreComputedTables
import pickle
from Move import Move


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

        self.enPassantStack = []
        self.castlingRightsStack = []
        self.halfMoveCounterStack = []
        self.moveStack = []

        self.bestMove = None

        try:
            self.pct: PreComputedTables = pickle.load(open("pctobject", "rb"))
        except FileNotFoundError:
            self.pct = PreComputedTables()
            pickle.dump(self.pct, open("pctobject", "wb"))

        self.setToFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def printBoard(self) -> None:
        print("  " + ("-" * 33))
        for i in range(64):
            if i % 8 == 0:
                print(f"{8 - (i // 8)} | ", end="")
            print(pieceToCharacter(self.board[i]) + " | ", end="")
            if i % 8 == 7:
                print("")
                print("  " + ("-" * 33))
        print("    a   b   c   d   e   f   g   h")
        print()
        print(
            "En Passant Square: "
            + (
                squareIndexToSquareName(self.enPassantSquare)
                if self.enPassantSquare
                else "-"
            )
        )
        print(f"Castling rights: {self.castlingRights}")
        print(f"Halfmove counter: {self.halfMoveCounter}")
        print(f"Fullmove counter: {self.fullMoveCounter}")
        print(f"To move: {'white' if self.currentTurn == WHITE else 'black'}")

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
        self.bitboards = [uint64(0)] * 23
        for squareIndex in range(64):
            piece = self.board[squareIndex]
            pieceBitBoard = self.bitboards[piece]
            self.bitboards[piece] = setBit(pieceBitBoard, squareIndex)

        self.updateOccupancyBitBoards()

    def updateOccupancyBitBoards(self) -> None:
        black_bitboard = uint64(0)
        for i in range(BLACK | PAWN, BLACK | KING + 1):
            black_bitboard = black_bitboard | self.bitboards[i]
        self.bitboards[BLACK] = black_bitboard

        white_bitboard = uint64(0)
        for i in range(WHITE | PAWN, WHITE | KING + 1):
            white_bitboard = white_bitboard | self.bitboards[i]
        self.bitboards[WHITE] = white_bitboard

        self.bitboards[ALL] = self.bitboards[WHITE] | self.bitboards[BLACK]

    def isSquareAttackedBy(self, square: int, bySide: int) -> bool:
        # Reference: https://www.chessprogramming.org/Square_Attacked_By
        otherSide = (BLACK + WHITE) - bySide
        occupied = self.bitboards[ALL]

        pawns = self.bitboards[bySide | PAWN]
        if self.pct.pawnAttackTable[otherSide][square] & pawns:
            return True

        knights = self.bitboards[bySide | KNIGHT]
        if self.pct.knightAttackTable[square] & knights:
            return True

        king = self.bitboards[bySide | KING]
        if self.pct.kingAttackTable[square] & king:
            return True

        bishopsQueens = self.bitboards[bySide | QUEEN] | self.bitboards[bySide | BISHOP]
        if self.pct.getBishopAttacks(square, occupied) & bishopsQueens:
            return True

        rooksQueens = self.bitboards[bySide | QUEEN] | self.bitboards[bySide | ROOK]
        if self.pct.getRookAttacks(square, occupied) & rooksQueens:
            return True

        return False

    def generateMoves(self) -> list[Move]:
        move_list = []
        move_list_count = 0

        for piece in ALL_PIECES:
            bitboard = self.bitboards[piece]

            if not bitboard:
                continue

            # Generate pawn white moves
            if self.currentTurn == WHITE:
                if piece == WHITE | PAWN:
                    while bitboard:
                        source_square = 63 - getLSBIndex(bitboard)
                        target_square = source_square - 8

                        if not (
                            target_square < 0
                            or target_square > 63
                            or getBit(self.bitboards[ALL], target_square)
                        ):
                            # Promoting push
                            if source_square > 7 and source_square < 16:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.nPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.bPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.rPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.qPromo,
                                        piece,
                                    )
                                )

                            else:
                                # Normal push
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.quietMove,
                                        piece,
                                    )
                                )
                                # Double push
                                if source_square > 47 and source_square < 56:
                                    target_square = target_square - 8
                                    if not getBit(self.bitboards[ALL], target_square):
                                        move_list.append(
                                            Move(
                                                source_square,
                                                target_square,
                                                Move.doublePawnPush,
                                                piece,
                                            )
                                        )

                        attacks = self.pct.pawnAttackTable[WHITE][source_square]
                        attacks &= self.bitboards[BLACK]

                        while attacks:
                            target_square = 63 - getLSBIndex(attacks)
                            targetPiece = self.board[target_square]

                            # Promoting capture
                            if source_square > 7 and source_square < 16:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.nPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.bPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.rPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.qPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )

                            # Normal capture
                            else:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.capture,
                                        piece,
                                        targetPiece,
                                    )
                                )

                            attacks = popLSB(attacks)

                        # En Passant Capture
                        if self.enPassantSquare:
                            enPassantAttacks = self.pct.pawnAttackTable[WHITE][
                                source_square
                            ] & setBit(uint64(0), self.enPassantSquare)
                            while enPassantAttacks:
                                target_square = 63 - getLSBIndex(enPassantAttacks)
                                targetPiece = BLACK | PAWN
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.epCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                enPassantAttacks = popLSB(enPassantAttacks)
                        bitboard = popLSB(bitboard)

                # Castling
                elif piece == WHITE | KING:
                    # Check kingside castling if relevant squares and empty and rights are still True
                    if self.castlingRights[WKINDEX] and not (
                        self.bitboards[ALL] & WKEMPTYBB
                    ):
                        # ensure squares are not under attack:
                        canCastle = True
                        for square in WKATTACKSQUARES:
                            if self.isSquareAttackedBy(square, BLACK):
                                canCastle = False
                                break

                        # Generate move if castle is legal
                        if canCastle:
                            move_list.append(
                                Move(
                                    squareNameToIndex("e1"),
                                    squareNameToIndex("g1"),
                                    Move.kingCastle,
                                    piece,
                                )
                            )

                    # Check queenside castling if relevant squares and empty and rights are still True
                    if self.castlingRights[WQINDEX] and not (
                        self.bitboards[ALL] & WQEMPTYBB
                    ):
                        # ensure squares are not under attack:
                        canCastle = True
                        for square in WQATTACKSQUARES:
                            if self.isSquareAttackedBy(square, BLACK):
                                canCastle = False
                                break

                        if canCastle:
                            move_list.append(
                                Move(
                                    squareNameToIndex("e1"),
                                    squareNameToIndex("c1"),
                                    Move.queenCastle,
                                    piece,
                                )
                            )

            # Generate black pawn moves
            elif self.currentTurn == BLACK:
                if piece == BLACK | PAWN:
                    while bitboard:
                        source_square = 63 - getLSBIndex(bitboard)
                        target_square = source_square + 8

                        if not (
                            target_square < 0
                            or target_square > 63
                            or getBit(self.bitboards[ALL], target_square)
                        ):
                            # Promoting push
                            if source_square > 47 and source_square < 56:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.nPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.bPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.rPromo,
                                        piece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.qPromo,
                                        piece,
                                    )
                                )
                            else:
                                # Normal push
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.quietMove,
                                        piece,
                                    )
                                )
                                # Double push
                                if source_square > 7 and source_square < 16:
                                    target_square = target_square + 8
                                    if not getBit(self.bitboards[ALL], target_square):
                                        move_list.append(
                                            Move(
                                                source_square,
                                                target_square,
                                                Move.doublePawnPush,
                                                piece,
                                            )
                                        )

                        attacks = self.pct.pawnAttackTable[BLACK][source_square]
                        attacks &= self.bitboards[WHITE]

                        while attacks:
                            target_square = 63 - getLSBIndex(attacks)
                            targetPiece = self.board[target_square]

                            # Promoting capture
                            if source_square > 47 and source_square < 56:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.nPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.bPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.rPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.qPromoCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )

                            # Normal capture
                            else:
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.capture,
                                        piece,
                                        targetPiece,
                                    )
                                )

                            attacks = popLSB(attacks)

                        # En Passant attacks:
                        if self.enPassantSquare:
                            enPassantAttacks = self.pct.pawnAttackTable[BLACK][
                                source_square
                            ] & setBit(uint64(0), self.enPassantSquare)
                            while enPassantAttacks:
                                target_square = 63 - getLSBIndex(enPassantAttacks)
                                targetPiece = WHITE | PAWN
                                move_list.append(
                                    Move(
                                        source_square,
                                        target_square,
                                        Move.epCapture,
                                        piece,
                                        targetPiece,
                                    )
                                )
                                enPassantAttacks = popLSB(enPassantAttacks)

                        bitboard = popLSB(bitboard)

                # Castling
                elif piece == BLACK | KING:
                    # Check kingside castling if relevant squares and empty and rights are still True
                    if self.castlingRights[BKINDEX] and not (
                        self.bitboards[ALL] & BKEMPTYBB
                    ):
                        # ensure squares are not under attack:
                        canCastle = True
                        for square in BKATTACKSQUARES:
                            if self.isSquareAttackedBy(square, WHITE):
                                canCastle = False
                                break

                        # Generate move if castle is legal
                        if canCastle:
                            move_list.append(
                                Move(
                                    squareNameToIndex("e8"),
                                    squareNameToIndex("g8"),
                                    Move.kingCastle,
                                    piece,
                                )
                            )

                    # Check kingside castling if relevant squares and empty and rights are still True
                    if self.castlingRights[BQINDEX] and not (
                        self.bitboards[ALL] & BQEMPTYBB
                    ):
                        # ensure squares are not under attack:
                        canCastle = True
                        for square in BQATTACKSQUARES:
                            if self.isSquareAttackedBy(square, WHITE):
                                canCastle = False
                                break

                        if canCastle:
                            move_list.append(
                                Move(
                                    squareNameToIndex("e8"),
                                    squareNameToIndex("c8"),
                                    Move.queenCastle,
                                    piece,
                                )
                            )

            if piece == self.currentTurn | KNIGHT:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)

                    attacks = self.pct.knightAttackTable[source_square] & ~(
                        self.bitboards[self.currentTurn]
                    )

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)

                        # Capture moves: The moves were filtered not to include same side piece captures
                        # so if the bit of the target square in all occupancies bitboard is set to one
                        # it is an opponent capture
                        if getBit(self.bitboards[ALL], target_square):
                            targetPiece = self.board[target_square]
                            move_list.append(
                                Move(
                                    source_square,
                                    target_square,
                                    Move.capture,
                                    piece,
                                    targetPiece,
                                )
                            )
                        else:
                            move_list.append(
                                Move(
                                    source_square, target_square, Move.quietMove, piece
                                )
                            )

                        attacks = popLSB(attacks)

                    bitboard = popLSB(bitboard)

            if piece == self.currentTurn | BISHOP:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)

                    attacks = self.pct.getBishopAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)

                        if getBit(self.bitboards[ALL], target_square):
                            targetPiece = self.board[target_square]
                            move_list.append(
                                Move(
                                    source_square,
                                    target_square,
                                    Move.capture,
                                    piece,
                                    targetPiece,
                                )
                            )
                        else:
                            move_list.append(
                                Move(
                                    source_square, target_square, Move.quietMove, piece
                                )
                            )

                        attacks = popLSB(attacks)

                    bitboard = popLSB(bitboard)

            if piece == self.currentTurn | ROOK:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)

                    attacks = self.pct.getRookAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)

                        if getBit(self.bitboards[ALL], target_square):
                            targetPiece = self.board[target_square]
                            move_list.append(
                                Move(
                                    source_square,
                                    target_square,
                                    Move.capture,
                                    piece,
                                    targetPiece,
                                )
                            )
                        else:
                            move_list.append(
                                Move(
                                    source_square, target_square, Move.quietMove, piece
                                )
                            )

                        attacks = popLSB(attacks)

                    bitboard = popLSB(bitboard)

            if piece == self.currentTurn | QUEEN:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)

                    attacks = self.pct.getQueenAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)

                        if getBit(self.bitboards[ALL], target_square):
                            targetPiece = self.board[target_square]
                            move_list.append(
                                Move(
                                    source_square,
                                    target_square,
                                    Move.capture,
                                    piece,
                                    targetPiece,
                                )
                            )
                        else:
                            move_list.append(
                                Move(
                                    source_square, target_square, Move.quietMove, piece
                                )
                            )

                        attacks = popLSB(attacks)

                    bitboard = popLSB(bitboard)

            if piece == self.currentTurn | KING:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)

                    attacks = self.pct.kingAttackTable[source_square] & ~(
                        self.bitboards[self.currentTurn]
                    )

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)

                        if getBit(self.bitboards[ALL], target_square):
                            targetPiece = self.board[target_square]
                            move_list.append(
                                Move(
                                    source_square,
                                    target_square,
                                    Move.capture,
                                    piece,
                                    targetPiece,
                                )
                            )
                        else:
                            move_list.append(
                                Move(
                                    source_square, target_square, Move.quietMove, piece
                                )
                            )

                        attacks = popLSB(attacks)

                    bitboard = popLSB(bitboard)
        return move_list

    def make_move(self, move: Move):
        start_square = move.start
        end_square = move.end
        piece = move.movingPiece
        capturedPiece = move.capturedPiece

        self.bitboards[piece] = setBit(self.bitboards[piece], end_square)
        self.board[start_square] = EMPTY
        self.bitboards[piece] = clearBit(self.bitboards[piece], start_square)
        self.board[end_square] = piece

        self.enPassantStack.append(self.enPassantSquare)

        if move.isDoublePush():
            offset = 8 if self.currentTurn == WHITE else -8
            self.enPassantSquare = end_square + offset
        else:
            self.enPassantSquare = None

        if move.isMoveCapture():
            if move.isEnPassant():
                offshift = 8 if findPieceColor(piece) == WHITE else -8
                self.board[end_square + offshift] = EMPTY
                self.bitboards[capturedPiece] = clearBit(
                    self.bitboards[capturedPiece], end_square + offshift
                )

            else:
                self.bitboards[capturedPiece] = clearBit(
                    self.bitboards[capturedPiece], end_square
                )

        if move.isPromotion():
            promotedPiece = move.promotedPiece()
            self.bitboards[piece] = clearBit(self.bitboards[piece], end_square)
            self.bitboards[promotedPiece] = setBit(
                self.bitboards[promotedPiece], end_square
            )
            self.board[end_square] = promotedPiece

        if move.isCastling():
            if self.currentTurn == WHITE:
                rook = WHITE | ROOK
                if move.flag == Move.kingCastle:
                    rookStart = squareNameToIndex("h1")
                    rookEnd = squareNameToIndex("f1")
                else:
                    rookStart = squareNameToIndex("a1")
                    rookEnd = squareNameToIndex("d1")
                self.bitboards[rook] = clearBit(self.bitboards[rook], rookStart)
                self.bitboards[rook] = setBit(self.bitboards[rook], rookEnd)
                self.board[rookStart] = EMPTY
                self.board[rookEnd] = rook

            if self.currentTurn == BLACK:
                rook = BLACK | ROOK
                if move.flag == Move.kingCastle:
                    rookStart = squareNameToIndex("h8")
                    rookEnd = squareNameToIndex("f8")
                else:
                    rookStart = squareNameToIndex("a8")
                    rookEnd = squareNameToIndex("d8")
                self.bitboards[rook] = clearBit(self.bitboards[rook], rookStart)
                self.bitboards[rook] = setBit(self.bitboards[rook], rookEnd)
                self.board[rookStart] = EMPTY
                self.board[rookEnd] = rook

        self.castlingRightsStack.append([right for right in self.castlingRights])

        if findPieceType(move.movingPiece) == KING:
            if self.currentTurn == WHITE:
                self.castlingRights[0] = False
                self.castlingRights[1] = False
            elif self.currentTurn == BLACK:
                self.castlingRights[2] = False
                self.castlingRights[3] = False

        if findPieceType(move.movingPiece) == ROOK:
            if start_square == squareNameToIndex("h1"):
                self.castlingRights[0] = False
            elif start_square == squareNameToIndex("a1"):
                self.castlingRights[1] = False
            elif start_square == squareNameToIndex("h8"):
                self.castlingRights[2] = False
            elif start_square == squareNameToIndex("a8"):
                self.castlingRights[3] = False

        if findPieceType(move.capturedPiece) == ROOK:
            if end_square == squareNameToIndex("h1"):
                self.castlingRights[0] = False
            elif end_square == squareNameToIndex("a1"):
                self.castlingRights[1] = False
            elif end_square == squareNameToIndex("h8"):
                self.castlingRights[2] = False
            elif end_square == squareNameToIndex("a8"):
                self.castlingRights[3]

        self.updateOccupancyBitBoards()

        self.halfMoveCounterStack.append(self.halfMoveCounter)
        if findPieceType(move.movingPiece) == PAWN or move.isMoveCapture():
            self.halfMoveCounter = 0
        else:
            self.halfMoveCounter += 1

        if self.currentTurn == BLACK:
            self.fullMoveCounter += 1

        self.currentTurn = (BLACK + WHITE) - self.currentTurn

        self.moveStack.append(move)

    def unmake_move(self) -> None:
        move = self.moveStack.pop()

        start_square = move.start
        end_square = move.end
        piece = move.movingPiece
        capturedPiece = move.capturedPiece

        self.bitboards[piece] = setBit(self.bitboards[piece], start_square)
        self.board[start_square] = piece
        self.bitboards[piece] = clearBit(self.bitboards[piece], end_square)
        self.board[end_square] = capturedPiece

        if move.isMoveCapture():
            if move.isEnPassant():
                self.board[end_square] = EMPTY
                offshift = 8 if findPieceColor(piece) == WHITE else -8
                self.board[end_square + offshift] = capturedPiece
                self.bitboards[capturedPiece] = setBit(
                    self.bitboards[capturedPiece], end_square + offshift
                )

            else:
                self.bitboards[capturedPiece] = setBit(
                    self.bitboards[capturedPiece], end_square
                )

        if move.isPromotion():
            promotedPiece = move.promotedPiece()
            self.bitboards[promotedPiece] = clearBit(
                self.bitboards[promotedPiece], end_square
            )

        self.enPassantSquare = self.enPassantStack.pop()

        if move.isCastling():
            turn = findPieceColor(move.movingPiece)
            if turn == WHITE:
                rook = WHITE | ROOK
                if move.flag == Move.kingCastle:
                    rookStart = squareNameToIndex("h1")
                    rookEnd = squareNameToIndex("f1")
                else:
                    rookStart = squareNameToIndex("a1")
                    rookEnd = squareNameToIndex("d1")
                self.bitboards[rook] = setBit(self.bitboards[rook], rookStart)
                self.bitboards[rook] = clearBit(self.bitboards[rook], rookEnd)
                self.board[rookStart] = rook
                self.board[rookEnd] = EMPTY

            if turn:
                rook = BLACK | ROOK
                if move.flag == Move.kingCastle:
                    rookStart = squareNameToIndex("h8")
                    rookEnd = squareNameToIndex("f8")
                else:
                    rookStart = squareNameToIndex("a8")
                    rookEnd = squareNameToIndex("d8")
                self.bitboards[rook] = setBit(self.bitboards[rook], rookStart)
                self.bitboards[rook] = clearBit(self.bitboards[rook], rookEnd)
                self.board[rookStart] = EMPTY
                self.board[rookEnd] = rook

        self.castlingRights = self.castlingRightsStack.pop()

        self.updateOccupancyBitBoards()

        self.halfMoveCounter = self.halfMoveCounterStack.pop()

        if findPieceColor(move.movingPiece) == BLACK:
            self.fullMoveCounter -= 1

        self.currentTurn = (BLACK + WHITE) - self.currentTurn

    def legalMoves(self) -> list[Move]:
        plmoves = self.generateMoves()
        lmoves = []
        for move in plmoves:
            self.make_move(move)
            if self.kingCanBeCaptured():
                self.unmake_move()
                continue
            lmoves.append(move)
            self.unmake_move()
        return lmoves

    def kingCanBeCaptured(self) -> bool:
        k = BLACK | KING
        K = WHITE | KING
        kingSquare = 63 - getLSBIndex(
            self.bitboards[k if self.currentTurn == WHITE else K]
        )
        return self.isSquareAttackedBy(kingSquare, self.currentTurn)

    def perft(self, depth: int) -> int:
        if depth == 0:
            return 1

        nodes = 0

        moves = self.generateMoves()
        for move in moves:
            self.make_move(move)
            if not self.kingCanBeCaptured():
                nodes += self.perft(depth - 1)
            self.unmake_move()
        return nodes

    def divide(self, depth: int) -> None:
        if depth == 0:
            raise "depth must be greater than 1 when calling divide"

        moves = self.legalMoves()
        for move in moves:
            self.make_move(move)
            print(f"{move}: {self.perft(depth - 1)}")
            self.unmake_move()

    def evaluate(self) -> int:
        score = 0

        for piece in BLACK_PIECES:
            score -= (
                self.bitboards[piece].bit_count()
                * MATERIALSCORETABLE[findPieceType(piece)]
            )

            bitboard = self.bitboards[piece]
            pieceType = findPieceType(piece)

            while bitboard:
                square = 63 - getLSBIndex(bitboard)
                pieceType = findPieceType(piece)
                score -= PIECESQUARESCORES[pieceType][
                    PIECESQUARESCORESINDEX[BLACK][square]
                ]

                bitboard = popLSB(bitboard)

        for piece in WHITE_PIECES:
            score += (
                self.bitboards[piece].bit_count()
                * MATERIALSCORETABLE[findPieceType(piece)]
            )

            bitboard = self.bitboards[piece]
            pieceType = findPieceType(piece)

            while bitboard:
                square = 63 - getLSBIndex(bitboard)
                pieceType = findPieceType(piece)
                score += PIECESQUARESCORES[pieceType][
                    PIECESQUARESCORESINDEX[WHITE][square]
                ]

                bitboard = popLSB(bitboard)

        return score if self.currentTurn == WHITE else -score

    def alphabeta(self, alpha: int, beta: int, depth: int, root: bool = False) -> None:
        if depth == 0:
            return self.evaluate()

        moves = self.generateMoves()

        best_sofar: Move = None

        for move in moves:
            self.make_move(move)
            if self.kingCanBeCaptured():
                self.unmake_move()
                continue

            score = -self.alphabeta(-beta, -alpha, depth - 1)
            self.unmake_move()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
                best_sofar = move

        if root:
            self.bestMove = best_sofar
        return alpha
