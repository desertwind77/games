#!/usr/bin/env python3

from gamelib.minimax import Minimax, CellType, Winner


class Board(Minimax):
    def __init__(self, row: int = 6, col: int = 7):
        super().__init__(row, col)
        self.row = row
        self.col = col


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
        for row in range(self.row):
            if self.is_cell_empty(row, col):
                return True
        return False


    def insert(self, player: CellType, col:int) -> None:
        '''
        Insert a chip into a column. The chip will be in the first empty cell.

        Args:
            player (Player): the player who inserts the chip
            col (int): the column to insert
        '''
        for row in range(self.row):
            if self.is_cell_empty(row, col):
                if row == self.row - 1:
                    # The last row
                    self.board[row, col] = player
                else:
                    if not self.is_cell_empty(row + 1, col):
                        self.board[row, col] = player


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
            player = CellType.COMPUTER if player == CellType.HUMAN else CellType.HUMAN
            self.show_board()

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


def main():
    board = Board()
    board.play()


if __name__ == '__main__':
    main()
