from numpy import uint64
from numpy.random import randint

WHITE = 0b01000
BLACK = 0b10000

PAWN = 0b00001
BISHOP = 0b00010
KNIGHT = 0b00011
ROOK = 0b00100
QUEEN = 0b00101
KING = 0b00110

EMPTY = 0b00000

PIECE_TO_CHARACTER = {
    PAWN: "p",
    BISHOP: "b",
    KNIGHT: "n",
    KING: "k",
    QUEEN: "q",
    ROOK: "r",
}
CHARACTER_TO_PIECE = {v: k for k, v in PIECE_TO_CHARACTER.items()}


def findPieceColor(piece: int) -> int:
    return piece & 0b11000


def findPieceType(piece: int) -> int:
    return piece & 0b00111


def pieceToCharacter(piece: int) -> str:
    if piece == EMPTY:
        return " "
    pieceColor = findPieceColor(piece)
    pieceType = findPieceType(piece)
    if pieceColor == WHITE:
        return PIECE_TO_CHARACTER[pieceType].upper()
    else:
        return PIECE_TO_CHARACTER[pieceType].lower()


def characterToPiece(char: str) -> int:
    if char.isupper():
        return WHITE | CHARACTER_TO_PIECE[char.lower()]
    else:
        return BLACK | CHARACTER_TO_PIECE[char]


def printBitBoard(bitboard: uint64) -> None:
    # prints the bitboard in a readable format for debugging

    a = format(bitboard, "#066b")
    for i in range(2, 66):
        if (i - 2) % 8 == 0:
            print(8 - ((i - 2) // 8), end="  ")
        print(a[i], end=" ")
        if ((i - 2) % 8) == 7:
            print("")
    print("")
    print("   a b c d e f g h")
    print()
    print(bitboard)
    print()
    print()


RANK_1 = 0x00000000000000FF

RANKS = [uint64(RANK_1 << 8 * i) for i in range(8)]


def rankNameToRankIndex(rank: str) -> int:
    # not sure if needed. converts rank from human format(1-8) to index(0-7)

    return int(rank) - 1


def rankIndexToRankName(rank: int) -> str:
    return str(rank + 1)


FILE_A = uint64(0x8080808080808080)
FILES = [uint64(FILE_A >> uint64(1 * i)) for i in range(8)]
FILE_H = FILES[7]
FILE_GH = FILES[7] | FILES[6]
FILE_AB = FILES[0] | FILES[1]


def fileNameToFileIndex(file: str) -> int:
    return ord(file) - 97


def fileIndexTofileName(file: int) -> str:
    return chr(file + 97)


def squareNameToIndex(squareName: str) -> int:
    fileName = squareName[0]
    rankName = squareName[1]
    fileIndex = fileNameToFileIndex(fileName)
    rankIndex = rankNameToRankIndex(rankName)

    # the rank indices in the chessboard from top to
    # bottom unlike the actual board when viewed from white's perspective
    return (7 - rankIndex) * 8 + fileIndex


# bit board operations
def setBit(bitboard: uint64, index: int) -> uint64:
    return bitboard | uint64(1) << uint64(63 - index)


def clearBit(bitboard: uint64, index: int) -> uint64:
    return bitboard & ~(uint64(1) << uint64(63 - index))


def getBit(bitboard: uint64, index: int) -> int:
    if bitboard & (uint64(1) << uint64(63 - index)):
        return 1
    else:
        return 0


def getLSBIndex(bitboard: uint64) -> int:
    # return 64 when bitboard is empty as otherwise python will throw RuntimeWarning
    if bitboard == uint64(0):
        return 64
    return ((bitboard & -bitboard) - uint64(1)).bit_count()


def popLSB(bitboard: uint64) -> uint64:
    idx = getLSBIndex(bitboard)
    return bitboard & (bitboard - uint64(1))


# direction functions
DIRECTION_OFFSETS = [-8, 8, -1, 1, -9, 7, -7, 9]


def north(bitboard: uint64) -> uint64:
    return (bitboard) << uint64(8)


def south(bitboard: uint64) -> uint64:
    return (bitboard) >> uint64(8)


def west(bitboard: uint64) -> uint64:
    return (bitboard & ~FILE_A) << uint64(1)


def east(bitboard: uint64) -> uint64:
    return (bitboard & ~FILE_H) >> uint64(1)


def northwest(bitBoard: uint64) -> uint64:
    return (bitBoard & ~FILE_A) << uint64(9)


def southwest(bitBoard: uint64) -> uint64:
    return (bitBoard & ~FILE_A) >> uint64(7)


def northeast(bitBoard: uint64) -> uint64:
    return (bitBoard & ~FILE_H) << uint64(7)


def southeast(bitboard: uint64) -> uint64:
    return (bitboard & ~FILE_H) >> uint64(9)


def random_uint64() -> uint64:
    return randint(pow(2, 64), dtype=uint64)


def random_uint64_fewbits() -> uint64:
    return random_uint64() & random_uint64() & random_uint64()


BMN = [
    9299934476606116096,
    577596067052028160,
    88253328302596,
    8865891501127,
    54131160770955264,
    7067273724143141888,
    774339688399428,
    4629775355660603392,
    1130469919826176,
    3461025145706251268,
    316667976614946,
    23708253160960,
    1130299060787456,
    633679542223874,
    9241704268582355076,
    5767433337786597376,
    307867622048000,
    4630879146031972424,
    2314886011861150784,
    72075323935687170,
    288265835674604032,
    2379589600013207556,
    4617317724033912880,
    9553274042364986369,
    852194794538048,
    4614154496129106432,
    2463487740516630592,
    5189277352152269064,
    11261200315187328,
    19151297844871238,
    2306001373382346754,
    5084158950967360,
    4786182710100168,
    1157708851316392197,
    305672839758080,
    9403656896910590024,
    2260596049444866,
    71468526600832,
    2286984330543361,
    67712325158961536,
    288371225678381314,
    185210539327168516,
    4612248969472377092,
    9532999066059805312,
    1497465604339220608,
    4616198448511730184,
    164689936866607234,
    2322244265124864,
    288899155209232384,
    596746812776294400,
    9799834997047429248,
    6341633433181093892,
    10413457054428628992,
    3459117461633695744,
    2305878748729245952,
    427023434584576,
    580120073069397024,
    5767141417451258112,
    144680350491345929,
    1130435409642788,
    72656286715615232,
    4613947168687128577,
    580628324040720,
    9016065149378624,
]

BISHOP_MAGIC_NUMBERS = uint64(BMN)

RMN = [
    145248235546626310,
    36046424093819420,
    63613379114173442,
    10385863707985973250,
    4684307937077239814,
    4612531028009963841,
    155392879450129537,
    18230130463735841,
    288586622222488064,
    4900479769868776960,
    140746078552192,
    1227521171709493376,
    4507998748147776,
    2314867802804060288,
    162305577169453248,
    2614378347916493568,
    9518358091628937220,
    576461851848638592,
    37717715733053444,
    576465150484185216,
    9851692906512396,
    3462177398198435908,
    5809643794454298657,
    13651811250503680,
    2449958752514738436,
    2500358228148488,
    2323998188186373120,
    144123986358305792,
    4512397876269056,
    9007337784217860,
    576495956078379008,
    18084769409531937,
    4504707728965700,
    9225626052882147344,
    9242514536442101888,
    2377909410082324608,
    10698325449787840,
    1161963892529759296,
    18084772624470016,
    144607775729680384,
    1128098985410705,
    4901187430054430864,
    3045137585333601280,
    91480467010750464,
    10278784720754688,
    297378863187496960,
    3170693017635930116,
    15150145980118073472,
    36310274147483904,
    39406505398700048,
    563018807378432,
    320318566447456260,
    293296999822917896,
    90212798763638784,
    581105364305453056,
    140749299673728,
    144117546039132676,
    432349982054547464,
    360292368270229760,
    9403555606517252102,
    360293472179064832,
    4683752687733309456,
    594492743535837184,
    684547694189875232,
]

ROOK_MAGIC_NUMBERS = [uint64(i) for i in RMN]
