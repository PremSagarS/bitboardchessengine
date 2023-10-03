from ChessFunctionsAndConstants import *
from random import randint


class PreComputedTables:
    def __init__(self) -> None:
        self.knightAttackTable = [uint64(0)] * 64
        self.pawnAttackTable = {WHITE: [uint64(0)] * 64, BLACK: [uint64(0)] * 64}
        self.pawnPushTable = {WHITE: [uint64(0)] * 64, BLACK: [uint64(0)] * 64}
        self.kingAttackTable = [uint64(0)] * 64

        self.numSquaresToEdge = [[] for i in range(64)]
        self.bishopOccupancyMask = [uint64(0)] * 64
        self.rookOccupancyMask = [uint64(0)] * 64

        self.bishopMagicNumbers = BISHOP_MAGIC_NUMBERS
        self.rookMagicNumbers = ROOK_MAGIC_NUMBERS

        self.bishopMagicBitBoards = [[uint64(0)] * 512 for i in range(64)]
        self.rookMagicBitBoards = [[uint64(0)] * 4096 for i in range(64)]

        self.computeKnightAttackTable()
        self.computePawnAttackTable()
        self.computePawnPushTable()
        self.computeKingAttackTable()

        self.computeNumSquaresToEdge()
        self.computeBishopOccupancyMasks()
        self.computeRookOccupancyMasks()

        # self.computeBishopMagicNumbers()
        # self.computeRookMagicNumbers()

        self.computeRookMagicBitBoards()
        self.computeBishopMagicBitboards()

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

    def computeNumSquaresToEdge(self) -> None:
        for rank in range(8):
            for file in range(8):
                northMax = rank
                southMax = 7 - rank
                eastMax = 7 - file
                westMax = file

                square = rank * 8 + file
                self.numSquaresToEdge[square] = [
                    northMax,
                    southMax,
                    westMax,
                    eastMax,
                    min(northMax, westMax),
                    min(southMax, westMax),
                    min(northMax, eastMax),
                    min(southMax, eastMax),
                ]

    def computeBishopOccupancyMasks(self) -> None:
        for i in range(64):
            attacks = uint64(0)
            for directionIndex in range(4, 8):
                for n in range(1, self.numSquaresToEdge[i][directionIndex]):
                    endSquareIndex = i + DIRECTION_OFFSETS[directionIndex] * n
                    attacks = setBit(attacks, endSquareIndex)
            self.bishopOccupancyMask[i] = attacks

    def computeRookOccupancyMasks(self) -> None:
        for i in range(64):
            attacks = uint64(0)
            for directionIndex in range(0, 4):
                for n in range(1, self.numSquaresToEdge[i][directionIndex]):
                    endSquareIndex = i + DIRECTION_OFFSETS[directionIndex] * n
                    attacks = setBit(attacks, endSquareIndex)
            self.rookOccupancyMask[i] = attacks

    def findBishopLegalMoveMask(self, startSquare: int, blockerbb: uint64) -> uint64:
        legalMoves = uint64(0)
        for directionIndex in range(4, 8):
            for n in range(1, self.numSquaresToEdge[startSquare][directionIndex] + 1):
                endSquareIndex = startSquare + DIRECTION_OFFSETS[directionIndex] * n
                legalMoves = setBit(legalMoves, endSquareIndex)
                if getBit(blockerbb, endSquareIndex) == (1):
                    break
        return legalMoves

    def findRookLegalMoveMask(self, startSquare: int, blockerbb: uint64) -> uint64:
        legalMoves = uint64(0)
        for directionIndex in range(0, 4):
            for n in range(1, self.numSquaresToEdge[startSquare][directionIndex] + 1):
                endSquareIndex = startSquare + DIRECTION_OFFSETS[directionIndex] * n
                legalMoves = setBit(legalMoves, endSquareIndex)
                if getBit(blockerbb, endSquareIndex) == (1):
                    break
        return legalMoves

    def createBlockerBitboard(
        self, occupancyMask: uint64, blockerPatternIndex: int
    ) -> uint64:
        occupancy = uint64(0)

        for count in range(0, occupancyMask.bit_count()):
            # index of first one in OCCUPANCY MASK
            square = getLSBIndex(occupancyMask)

            # change the first one to zero to get index of next one on the next iteration
            occupancyMask = popLSB(occupancyMask)

            # blockerpatternindex & (1 << count) returns True if there is a one on the
            # position whose index is denoted by count. In that case the relevant square in occupancy
            # is set to one.
            if blockerPatternIndex & (1 << count):
                occupancy |= uint64(1) << uint64(square)

        return occupancy

    def bishopMagicFinder(self, sq: int) -> uint64:
        mask = uint64(0)
        b = [uint64(0)] * 4096
        a = [uint64(0)] * 4096
        used = [uint64(0)] * 4096
        mask = uint64(0)

        neededBits = self.bishopOccupancyMask[sq].bit_count()
        mask = self.bishopOccupancyMask[sq]
        n = mask.bit_count()

        for i in range(1 << n):
            b[i] = self.createBlockerBitboard(mask, i)
            a[i] = self.findBishopLegalMoveMask(sq, b[i])

        for k in range(1000000):
            magic = random_uint64_fewbits()
            if (((mask * magic) & 0xFF00000000000000).bit_count()) < 6:
                continue
            for i in range(4096):
                used[i] = uint64(0)
            i = 0
            fail = 0
            while not fail and i < (1 << n):
                j = int((b[i] * magic) >> uint64(64 - neededBits))
                if used[j] == uint64(0):
                    used[j] = a[i]
                elif used[j] != a[i]:
                    fail = 1
                i += 1
            if not fail:
                return magic

        raise Exception("Failed to find magic number")

    def rookMagicFinder(self, sq: int) -> uint64:
        mask = uint64(0)
        b = [uint64(0)] * 4096
        a = [uint64(0)] * 4096
        used = [uint64(0)] * 4096
        mask = uint64(0)

        neededBits = self.rookOccupancyMask[sq].bit_count()
        mask = self.rookOccupancyMask[sq]
        n = mask.bit_count()

        for i in range(1 << n):
            b[i] = self.createBlockerBitboard(mask, i)
            a[i] = self.findRookLegalMoveMask(sq, b[i])

        for k in range(1000000):
            magic = random_uint64_fewbits()
            if (((mask * magic) & 0xFF00000000000000).bit_count()) < 6:
                continue
            for i in range(4096):
                used[i] = uint64(0)
            i = 0
            fail = 0
            while not fail and i < (1 << n):
                j = int((b[i] * magic) >> uint64(64 - neededBits))
                if used[j] == uint64(0):
                    used[j] = a[i]
                elif used[j] != a[i]:
                    fail = 1
                i += 1
            if not fail:
                return magic
        print(self.rookMagicNumbers)
        raise Exception("Failed to find magic number")

    def computeBishopMagicNumbers(self) -> None:
        for square in range(64):
            self.bishopMagicNumbers[square] = self.bishopMagicFinder(square)
            print(f"Found for square number {square}")

    def computeRookMagicNumbers(self) -> None:
        for square in range(64):
            self.rookMagicNumbers[square] = self.rookMagicFinder(square)
            print(f"Found for square number {square}")

    def computeBishopMagicBitboards(self) -> None:
        for square in range(64):
            occupancyMask = self.bishopOccupancyMask[square]
            n = occupancyMask.bit_count()
            numPatterns = 1 << n
            magicnumber = self.bishopMagicNumbers[square]

            blockers = [uint64(0)] * 4096
            legalMoveMasks = [uint64(0)] * 4096

            for i in range(numPatterns):
                blockers[i] = self.createBlockerBitboard(occupancyMask, i)
                legalMoveMasks[i] = self.findBishopLegalMoveMask(square, blockers[i])

            for i in range(numPatterns):
                j = int((blockers[i] * magicnumber) >> uint64(64 - n))
                if self.bishopMagicBitBoards[square][j] == uint64(0):
                    self.bishopMagicBitBoards[square][j] = legalMoveMasks[i]
                elif self.bishopMagicBitBoards[square][j] != legalMoveMasks[i]:
                    raise Exception("Magic number does not work as intended")

    def computeRookMagicBitBoards(self) -> None:
        for square in range(64):
            occupancyMask = self.rookOccupancyMask[square]
            n = occupancyMask.bit_count()
            numPatterns = 1 << n
            magicnumber = self.rookMagicNumbers[square]

            blockers = [uint64(0)] * 4096
            legalMoveMasks = [uint64(0)] * 4096

            for i in range(numPatterns):
                blockers[i] = self.createBlockerBitboard(occupancyMask, i)
                legalMoveMasks[i] = self.findRookLegalMoveMask(square, blockers[i])

            for i in range(numPatterns):
                j = int((blockers[i] * magicnumber) >> uint64(64 - n))
                if self.rookMagicBitBoards[square][j] == uint64(0):
                    self.rookMagicBitBoards[square][j] = legalMoveMasks[i]
                elif self.rookMagicBitBoards[square][j] != legalMoveMasks[i]:
                    print(square, numPatterns, i)
                    raise Exception("Magic number does not work as intended")
