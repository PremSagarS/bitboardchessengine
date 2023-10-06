from Board import *
from ChessFunctionsAndConstants import *
from Move import *
from PreComputedTables import *


global board


def parse_move(move_string: str) -> Move | bool:
    source_square = squareNameToIndex(move_string[0:2])
    target_square = squareNameToIndex(move_string[2:4])

    moves = board.generateMoves()
    for move in moves:
        if repr(move) == move_string:
            return move

    return False


if __name__ == "__main__":
    board = Board()
    board.setToFen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
    board.printBoard()
    move = parse_move(input())
    if move:
        board.make_move(move)
        board.printBoard()
    else:
        print("Illegal move")
