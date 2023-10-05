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

        try:
            self.pct: PreComputedTables = pickle.load(open("pctobject", "rb"))
        except FileNotFoundError:
            self.pct = PreComputedTables()
            pickle.dump(self.pct, open("pctobject", "Wb"))

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

        rooksQueens = self.bitboards[bySide | QUEEN] | self.bitboards[bySide | BISHOP]
        if self.pct.getRookAttacks(square, occupied) & rooksQueens:
            return True

        return False

    def generateMoves(self):
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
                        ssname = squareIndexToSquareName(source_square)
                        target_square = source_square - 8
                        tsname = squareIndexToSquareName(target_square)

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
                                    tsname = squareIndexToSquareName(target_square)
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
                            tsname = squareIndexToSquareName(target_square)
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
                                tsname = squareIndexToSquareName(target_square)
                                targetPiece = self.board[target_square]
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
                                    source_square,
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
                                    source_square,
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
                        ssname = squareIndexToSquareName(source_square)
                        target_square = source_square + 8
                        tsname = squareIndexToSquareName(target_square)

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
                                    tsname = squareIndexToSquareName(target_square)
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
                            tsname = squareIndexToSquareName(target_square)

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
                                target_square = 63 - getLSBIndex(attacks)
                                tsname = squareIndexToSquareName(target_square)
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
                                    source_square,
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
                                    source_square,
                                    squareNameToIndex("c8"),
                                    Move.queenCastle,
                                    piece,
                                )
                            )

            if piece == self.currentTurn | KNIGHT:
                while bitboard:
                    source_square = 63 - getLSBIndex(bitboard)
                    ssname = squareIndexToSquareName(source_square)

                    attacks = self.pct.knightAttackTable[source_square] & ~(
                        self.bitboards[self.currentTurn]
                    )

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)
                        tsname = squareIndexToSquareName(target_square)

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
                    ssname = squareIndexToSquareName(source_square)

                    attacks = self.pct.getBishopAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)
                        tsname = squareIndexToSquareName(target_square)

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
                    ssname = squareIndexToSquareName(source_square)

                    attacks = self.pct.getRookAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)
                        tsname = squareIndexToSquareName(target_square)

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
                    ssname = squareIndexToSquareName(source_square)

                    attacks = self.pct.getQueenAttacks(
                        source_square, self.bitboards[ALL]
                    ) & ~(self.bitboards[self.currentTurn])

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)
                        tsname = squareIndexToSquareName(target_square)

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
                    ssname = squareIndexToSquareName(source_square)

                    attacks = self.pct.kingAttackTable[square] & ~(
                        self.bitboards[self.currentTurn]
                    )

                    while attacks:
                        target_square = 63 - getLSBIndex(attacks)
                        tsname = squareIndexToSquareName(target_square)

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
