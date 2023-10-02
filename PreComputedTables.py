from ChessFunctionsAndConstants import *


class PreComputedTables:
    def __init__(self) -> None:
        self.knightAttackTable = [uint64(0)] * 64
        self.pawnAttackTable = {WHITE: [uint64(0)] * 64, BLACK: [uint64(0)] * 64}
        self.pawnPushTable = {WHITE: [uint64(0)] * 64, BLACK: [uint64(0)] * 64}
        self.kingAttackTable = [uint64(0)] * 64
        self.bishopMovementMask = [uint64(0)] * 64
        self.rookMovementMask = [uint64(0)] * 64
        self.queenMovementMask = [uint64(0)] * 64

        self.computeKnightAttackTable()
        self.computePawnAttackTable()
        self.computePawnPushTable()
        self.computeKingAttackTable()

        self.computeBishopMovementMasks()
        self.computeRookMovementMasks()
        self.computeQueenMovementMasks()

    def computeKnightAttackTable(self) -> None:
        for i in range(64):
            bitBoard = setBit(uint64(0), i)
            attacks = (
                (((bitBoard >> uint64(6)) | (bitBoard << uint64(10))) & ~FILE_GH)
                | (((bitBoard >> uint64(10)) | (bitBoard << uint64(6))) & ~FILE_AB)
                | (((bitBoard >> uint64(15)) | (bitBoard << uint64(17))) & ~FILE_H)
                | (((bitBoard >> uint64(17)) | (bitBoard << uint64(15))) & ~FILE_A)
            )
            self.knightAttackTable[i] = attacks

    def computePawnAttackTable(self) -> None:
        for i in range(8, 56):
            bitBoard = setBit(uint64(0), i)
            attacks = northeast(bitBoard) | northwest(bitBoard)
            self.pawnAttackTable[WHITE][i] = attacks

        for i in range(8, 56):
            bitBoard = setBit(uint64(0), i)
            attacks = southeast(bitBoard) | southwest(bitBoard)
            self.pawnAttackTable[BLACK][i] = attacks

    def computePawnPushTable(self) -> None:
        for i in range(8, 56):
            bitBoard = setBit(uint64(0), i)
            pushes = north(bitBoard)
            self.pawnPushTable[WHITE][i] = pushes

        for i in range(8, 56):
            bitBoard = setBit(uint64(0), i)
            pushes = south(bitBoard)
            self.pawnPushTable[BLACK][i] = pushes

    def computeKingAttackTable(self) -> None:
        for i in range(64):
            bitBoard = setBit(uint64(0), i)
            moves = uint64(0)
            for directionFunction in [
                north,
                south,
                west,
                east,
                northwest,
                northeast,
                southeast,
                southwest,
            ]:
                moves = moves | directionFunction(bitBoard)
            self.kingAttackTable[i] = moves

    def computeBishopMovementMasks(self) -> None:
        for i in range(64):
            bitBoard = setBit(uint64(0), i)
            finalMoves = uint64(0)
            for directionFunction in [northwest, northeast, southwest, southeast]:
                moveBitBoard = directionFunction(bitBoard)
                while True:
                    newMoveBitBoard = moveBitBoard | directionFunction(moveBitBoard)
                    if newMoveBitBoard == moveBitBoard:
                        break
                    moveBitBoard = newMoveBitBoard
                finalMoves = finalMoves | moveBitBoard
            self.bishopMovementMask[i] = finalMoves

    def computeRookMovementMasks(self) -> None:
        for i in range(64):
            bitBoard = setBit(uint64(0), i)
            finalMoves = uint64(0)
            for directionFunction in [north, south, west, east]:
                moveBitBoard = directionFunction(bitBoard)
                while True:
                    newMoveBitBoard = moveBitBoard | directionFunction(moveBitBoard)
                    if newMoveBitBoard == moveBitBoard:
                        break
                    moveBitBoard = newMoveBitBoard
                finalMoves = finalMoves | moveBitBoard
            self.rookMovementMask[i] = finalMoves

    def computeQueenMovementMasks(self) -> None:
        for i in range(64):
            self.queenMovementMask[i] = (
                self.bishopMovementMask[i] | self.rookMovementMask[i]
            )
