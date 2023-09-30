from numpy import uint64

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
        print(a[i], end="")
        if ((i - 2) % 8) == 7:
            print("")


RANK_1 = 0x00000000000000FF

RANKS = [uint64(RANK_1 << 8 * i) for i in range(8)]


def rankNameToRankIndex(rank: str) -> int:
    # not sure if needed. converts rank from human format(1-8) to index(0-7)

    return int(rank) - 1


FILE_A = uint64(0x8080808080808080)
FILES = [uint64(FILE_A >> uint64(1 * i)) for i in range(8)]
FILE_H = FILES[7]
FILE_GH = FILES[7] | FILES[6]
FILE_AB = FILES[0] | FILES[1]


def fileNameToFileIndex(file: str) -> int:
    return ord(file) - 97


def squareNameToIndex(squareName: str) -> int:
    fileName = squareName[0]
    rankName = squareName[1]
    fileIndex = fileNameToFileIndex(fileName)
    rankIndex = rankNameToRankIndex(rankName)

    # the rank indices in the chessboard from top to
    # bottom unlike the actual board when viewed from white's perspective
    return (rankIndex - 7) * 8 + fileIndex


def setBit(bitboard: uint64, index: int) -> uint64:
    return bitboard | uint64(1) << uint64(63 - index)


def clearBit(bitboard: uint64, index: int) -> uint64:
    return bitboard & ~(uint64(1) << uint64(63 - index))
