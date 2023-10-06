from ChessFunctionsAndConstants import *
from numpy import uint8


class Move:
    # Flag possible values
    # See: https://www.chessprogramming.org/Encoding_Moves

    quietMove = uint8(0b0000)
    doublePawnPush = uint8(0b0001)
    kingCastle = uint8(0b0010)
    queenCastle = uint8(0b0011)
    capture = uint8(0b0100)
    epCapture = uint8(0b0101)
    nPromo = uint8(0b1000)
    bPromo = uint8(0b1001)
    rPromo = uint8(0b1010)
    qPromo = uint8(0b1011)
    nPromoCapture = uint8(0b1100)
    bPromoCapture = uint8(0b1101)
    rPromoCapture = uint8(0b1110)
    qPromoCapture = uint8(0b1111)

    def __init__(
        self,
        start: int,
        end: int,
        flag: int,
        movingPiece: int,
        capturedPiece: int = EMPTY,
    ) -> None:
        self.start = start
        self.end = end
        self.flag = flag
        self.movingPiece = movingPiece
        self.capturedPiece = capturedPiece

    def isMoveQuiet(self) -> bool:
        return self.flag == self.quietMove

    def isMoveCapture(self) -> bool:
        return self.flag & self.capture

    def promotedPiece(self) -> int:
        color = findPieceColor(self.movingPiece)
        if self.flag == self.nPromo or self.flag == self.nPromoCapture:
            return color | KNIGHT

        elif self.flag == self.bPromo or self.flag == self.bPromoCapture:
            return color | BISHOP

        elif self.flag == self.rPromo or self.flag == self.rPromoCapture:
            return color | ROOK

        elif self.flag == self.qPromo or self.flag == self.qPromoCapture:
            return color | QUEEN

        else:
            return EMPTY

    def isEnPassant(self) -> bool:
        return self.flag == self.epCapture

    def isDoublePush(self) -> bool:
        return self.doublePawnPush == self.flag

    def isPromotion(self) -> bool:
        return self.flag & uint8(0b1000)

    def isCastling(self) -> bool:
        return self.flag == self.kingCastle or self.flag == self.queenCastle

    def __repr__(self) -> str:
        startSquare = squareIndexToSquareName(self.start)
        endSquare = squareIndexToSquareName(self.end)
        if not self.isPromotion():
            return startSquare + endSquare
        promotedPieceText = {KNIGHT: "n", QUEEN: "q", BISHOP: "b", ROOK: "r"}[
            findPieceType(self.promotedPiece())
        ]
        return startSquare + endSquare + promotedPieceText
