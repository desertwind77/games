#!/usr/bin/env python3
import argparse
import math
from typing import Optional

from gamelib.minimax import Minimax, CellType, Winner


class Board(Minimax):
    def __init__(self, row: int = 6, col: int = 7, max_depth: int = 3):
        super().__init__(row, col)
        self.row = row
        self.col = col
        self.max_depth = max_depth


    def cell_char(self, cell_type: CellType) -> str:
        cell_dict = {
            CellType.EMPTY: ' ',
            CellType.HUMAN: 'R',
            CellType.COMPUTER: 'Y',
        }
        return cell_dict[cell_type]


    def is_cell_empty(self, row: int, col: int) -> bool:
        '''
        Check if a cell in the board is empty.

        Args:
            row (int): row
            col (int): column

        Return:
            True if the cell is empty
        '''
        return self.board[row, col] == CellType.EMPTY


    def has_empty_cell(self, col: int) -> bool:
        '''
        Check if a column in the board has an empty cell.

        Args:
            col (int): column

        Return:
            True if there is an empty cell in the column
        '''
        return self.next_open_row(col) is not None


    def next_open_row(self, col: int) -> Optional[int]:
        '''Return the lowest open row index in a column, or None if full.'''
        if col < 0 or col >= self.col:
            return None
        for row in reversed(range(self.row)):
            if self.is_cell_empty(row, col):
                return row
        return None


    def insert(self, player: CellType, col:int) -> None:
        '''
        Insert a chip into a column. The chip will be in the first empty cell.

        Args:
            player (Player): the player who inserts the chip
            col (int): the column to insert
        '''
        if (row := self.next_open_row(col)) is not None:
            self.board[row, col] = player
            if player == CellType.HUMAN:
                self.last_human_move = (row, col)
            else:
                self.last_computer_move = (row, col)


    def best_move(self) -> None:
        '''Choose the best move for the computer using depth-limited minimax.'''
        best_score = -math.inf
        best_col = None

        for col in range(self.col):
            if (row := self.next_open_row(col)) is None:
                continue
            self.board[row, col] = CellType.COMPUTER
            score = self.minimax(0, False, max_depth=self.max_depth)
            self.board[row, col] = CellType.EMPTY

            if score > best_score:
                best_score = score
                best_col = col

        if best_col is not None:
            drop_row = self.next_open_row(best_col)
            if drop_row is not None:
                self.board[drop_row, best_col] = CellType.COMPUTER
                self.last_computer_move = (drop_row, best_col)


    def check_winner(self) -> Winner:
        for row in range(self.row):
            for col in range(self.col - 3):
                chips = set(self.board[row, col + i] for i in range(4))
                if len(chips) == 1:
                    if ( winner := chips.pop() ) != CellType.EMPTY:
                        return Winner.HUMAN if winner == CellType.HUMAN \
                                else Winner.COMPUTER

        for col in range(self.col):
            for row in range(self.row - 3):
                chips = set(self.board[row + i, col] for i in range(4))
                if len(chips) == 1:
                    if ( winner := chips.pop() ) != CellType.EMPTY:
                        return Winner.HUMAN if winner == CellType.HUMAN \
                                else Winner.COMPUTER

        for row in range(self.row - 3):
            for col in range(self.col - 3):
                chips = set(self.board[row + i, col + i] for i in range(4))
                if len(chips) == 1:
                    if ( winner := chips.pop() ) != CellType.EMPTY:
                        return Winner.HUMAN if winner == CellType.HUMAN \
                                else Winner.COMPUTER

        for row in range(self.row - 3):
            for col in range(3, self.col):
                chips = set(self.board[row + i, col - i] for i in range(4))
                if len(chips) == 1:
                    if ( winner := chips.pop() ) != CellType.EMPTY:
                        return Winner.HUMAN if winner == CellType.HUMAN \
                                else Winner.COMPUTER

        # Check if the game ends in a tie
        empty_count = [self.board[r][c]
                       for r in range(self.row)
                       for c in range(self.col)
                       if self.board[r, c] == CellType.EMPTY]
        if len(empty_count) == 0:
            return Winner.TIE
        return Winner.NONE


    def play(self):
        self.show_board()

        player = CellType.HUMAN
        while True:
            if player == CellType.HUMAN:
                input_str = input("Enter the column number or 'q' to quit: ").strip()
                if input_str == 'q':
                    return

                try:
                    col = int(input_str)
                except ValueError:
                    continue

                if not self.has_empty_cell(col):
                    continue

                self.insert(player, col)
            else:
                print("Computer's turn\n")
                self.best_move()

            self.show_board()

            winner = self.check_winner()
            if winner == Winner.NONE:
                player = CellType.COMPUTER if player == CellType.HUMAN else CellType.HUMAN
                continue

            message_dict = {
                Winner.TIE: 'Tie!',
                Winner.HUMAN: 'You won!',
                Winner.COMPUTER: 'Computer won!',
            }
            print(message_dict[winner])
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--max-depth', type=int, default=3,
                        help='Max search depth for minimax (default: 3)')
    args = parser.parse_args()

    board = Board(max_depth=args.max_depth)
    board.play()


if __name__ == '__main__':
    main()
