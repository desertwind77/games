'''Shared Minimax game engine with alpha-beta pruning.

Games can subclass `Minimax` and provide board-specific winner detection and
rendering helpers while reusing the core search routine.
'''
from enum import Enum
from typing import Optional
import math

# pylint: disable=import-error
import numpy as np


class CellType(Enum):
    EMPTY = 0
    HUMAN = 1
    COMPUTER = 2


class Winner(Enum):
    NONE = 0
    TIE = 1
    HUMAN = 2
    COMPUTER = 3


class Minimax:
    '''Base class for grid-based, two-player, perfect-information games.'''
    def __init__(self, row, col):
        '''Initialize an empty board of the configured shape.'''
        self.row = row
        self.col = col
        self.board = np.full((self.row, self.col), CellType.EMPTY)

    def minimax(self, depth: int, is_maximizing: bool, alpha: float = -math.inf,
                beta: float = math.inf, max_depth: Optional[int] = None) -> float:
        '''An implementation of the Minimax algorithm with alpha-beta pruning

        Arguments:
            depth (int): the current depth in the decision tree; used for
                         depth-weighted scoring and can be used to bound search
                         for deeper games to keep response times reasonable

            is_maximizing (bool): operating as a maximizer or a minimizer
            alpha (float): best already explored option along the path to the root for maximizer
            beta (float): best already explored option along the path to the root for minimizer
            max_depth (Optional[int]): optional depth limit to cap search for
                                        large branching games

        Returns:
            (int) the score of this path. Scores are depth-weighted to favor
            faster wins and slower losses: positive for computer wins, negative
            for human wins, and 0 for ties.
        '''
        if (winner := self.check_winner()) != Winner.NONE:
            if winner == Winner.TIE:
                return 0
            if winner == Winner.HUMAN:
                return depth - 10
            return 10 - depth

        if max_depth is not None and depth >= max_depth:
            return 0

        if is_maximizing:
            best_score = -math.inf
            for row in range(self.row):
                for col in range(self.col):
                    if self.board[row, col] != CellType.EMPTY:
                        continue
                    self.board[row, col] = CellType.COMPUTER
                    score = self.minimax(depth + 1, False, alpha, beta, max_depth)
                    self.board[row, col] = CellType.EMPTY

                    best_score = max(best_score, score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        # Beta cut-off: opponent already has a better option.
                        return best_score
        else:
            best_score = math.inf
            for row in range(self.row):
                for col in range(self.col):
                    if self.board[row, col] != CellType.EMPTY:
                        continue
                    self.board[row, col] = CellType.HUMAN

                    score = self.minimax(depth + 1, True, alpha, beta, max_depth)
                    best_score = min(best_score, score)
                    self.board[row, col] = CellType.EMPTY
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        # Alpha cut-off: maximizing player found a path that
                        # avoids this subtree.
                        return best_score
        return best_score

    def check_winner(self) -> Winner:
        '''Check who is the winner'''
        raise NotImplementedError

    def cell_char(self, cell_type: CellType) -> str:
        '''Translate a cell enum into a display character.'''
        raise NotImplementedError

    def show_board(self):
        '''Draw the board on the console screen'''
        col = [str(i) for i in range(self.col)]
        col_str = '    ' + '   '.join(col)
        print(col_str)
        for row in range(self.row):
            cells = [self.cell_char(i) for i in self.board[row]]
            content = f'{row} | ' + ' | '.join(cells) + ' |'
            print(content)
        print()
