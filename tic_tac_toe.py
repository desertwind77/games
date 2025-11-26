#!/usr/bin/env python
'''
A script to play Tic Tac Toe against the computer.
This script demonstrates the Minimax algorithm.
'''
import argparse
import math
import random
import uuid
import sys

from gamelib.minimax import Minimax, CellType, Winner


class TicTacToe(Minimax):
    '''The classic Tic Tac Toe board game built on the Minimax engine.'''
    def __init__(self, size: int = 3, max_depth: int = 3) -> None:
        '''Constructor

        Args:
            size (int): the size of the board
        '''
        super().__init__(size, size)
        self.size = size
        self.max_depth = max_depth

    def cell_char(self, cell_type: CellType) -> str:
        '''Render a cell value into a printable character.'''
        cell_dict = {
            CellType.EMPTY: ' ',
            CellType.HUMAN: 'O',
            CellType.COMPUTER: 'X',
        }
        return cell_dict[cell_type]

    def check_winner(self) -> Winner:
        '''Check if there is a winner

        Returns:
            the winner
        '''
        # Horizontal lines
        for row in range(self.size):
            values = set(self.board[row, i] for i in range(self.size))
            if len(values) == 1:
                if (winner := values.pop()) != CellType.EMPTY:
                    return Winner.HUMAN if winner == CellType.HUMAN \
                            else Winner.COMPUTER

        # Vertical lines
        for col in range(self.size):
            values = set(self.board[i, col] for i in range(self.size))
            if len(values) == 1:
                if (winner := values.pop()) != CellType.EMPTY:
                    return Winner.HUMAN if winner == CellType.HUMAN \
                            else Winner.COMPUTER

        # Diagonals
        values = set(self.board[i, i] for i in range(self.size))
        if len(values) == 1:
            if (winner := values.pop()) != CellType.EMPTY:
                return Winner.HUMAN if winner == CellType.HUMAN else Winner.COMPUTER
        values = set(self.board[i][self.size - i - 1] for i in range(self.size))
        if len(values) == 1:
            if (winner := values.pop()) != CellType.EMPTY:
                return Winner.HUMAN if winner == CellType.HUMAN else Winner.COMPUTER

        # Check if the game ends in a tie
        empty_count = [self.board[r][c]
                       for r in range(self.size)
                       for c in range(self.size)
                       if self.board[r, c] == CellType.EMPTY]
        if len(empty_count) == 0:
            return Winner.TIE
        return Winner.NONE

    def best_move(self) -> None:
        '''For the computer to choose his next best move, one with the
        highest score according to the minimax algorithm'''
        best_score = -math.inf
        move_row = move_col = None
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row, col] != CellType.EMPTY:
                    continue
                self.board[row, col] = CellType.COMPUTER
                score = self.minimax(0, False, max_depth=self.max_depth)
                self.board[row, col] = CellType.EMPTY

                if score >= best_score:
                    best_score = score
                    move_row, move_col = row, col
        self.board[move_row, move_col] = CellType.COMPUTER
        self.last_computer_move = (move_row, move_col)

    def random_move(self) -> None:
        '''Choose an empty cell randomly'''
        empty_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row, col] == CellType.EMPTY:
                    empty_cells.append((row, col))
        r, c = random.choice(empty_cells)
        self.board[r][c] = CellType.COMPUTER
        self.last_computer_move = (r, c)

    def coin_toss(self) -> bool:
        '''Toss a coin

        Returns:
            (bool) either True or False 50% of the times
        '''
        gen_id = str(uuid.uuid4())
        while not gen_id[0].isnumeric():
            gen_id = str(uuid.uuid4())
        return int(gen_id[0]) >= 5

    def make_human_move(self) -> None:
        '''Prompt for and place the human player's move.'''
        while True:
            try:
                input_str = input("Enter row and col (e.g. 1 2) or q to quit: ").strip()
                if input_str == 'q':
                    sys.exit(0)
                row_str, col_str = input_str.split(' ')
                row, col = int(row_str), int(col_str)
            except ValueError:
                continue
            if (row >= self.size or col >= self.size) or \
                    self.board[row, col] != CellType.EMPTY:
                continue
            self.board[row, col] = CellType.HUMAN
            self.last_human_move = (row, col)
            break

    def make_computer_move(self, difficulty: int) -> None:
        '''Select the computer's move using the requested difficulty profile.'''
        print("Machine's turn\n")

        if difficulty == 3:
            self.best_move()
        elif difficulty == 2:
            if self.coin_toss():
                self.best_move()
            else:
                self.random_move()
        else:
            self.random_move()

    def play(self, difficulty: int, human_first: bool = True) -> None:
        '''Play the game against the computer

        Args:
            difficulty (int): difficulty level
            human_first (bool): the first move is for the human or machine
        '''
        count = 0
        human = human_first

        if human:
            self.show_board()

        while count < self.size * self.size:
            if human:
                self.make_human_move()
                print()
            else:
                self.make_computer_move(difficulty)
            self.show_board()
            count += 1
            human = not human

            winner = self.check_winner()
            if winner == Winner.NONE:
                continue
            message_dict = {
                Winner.TIE: 'Tie!',
                Winner.HUMAN: 'You won!',
                Winner.COMPUTER: 'Computer won!',
            }
            print(message_dict[winner])
            break


def process_arguments() -> argparse.Namespace:
    '''Process commandline arguments

    return:
        a Parameters object which contains all command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--difficulty', action='store', dest='difficulty',
                        choices=['1', '2', '3'], default='3',
                        help='Choose the difficulty level')
    parser.add_argument('-H', '--human-first', action='store_true', dest='human_first',
                        help='Let the human play first')
    parser.add_argument('-m', '--max-depth', type=int, default=3,
                        help='Max search depth for minimax (default: 3)')
    return parser.parse_args()


def main():
    '''The main program'''
    args = process_arguments()
    game = TicTacToe(max_depth=args.max_depth)
    difficulty = int(args.difficulty)
    game.play(difficulty=difficulty, human_first=args.human_first)


if __name__ == '__main__':
    main()
