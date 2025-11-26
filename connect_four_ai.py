#!/usr/bin/env python3
"""Standalone Connect Four with a faster alpha-beta AI.

Features:
- Bitboard representation for quick move generation and win checks.
- Alpha-beta search with transposition table.
- Center-first move ordering and heuristic scoring of 4-length windows.
- Configurable search depth and optional deterministic first-player override.
"""
from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Board geometry
WIDTH = 7
HEIGHT = 6
HEIGHT1 = HEIGHT + 1  # include sentinel row
SIZE = WIDTH * HEIGHT1

# Precompute column bitmasks for bitboard operations
COLUMN_MASKS = [((1 << HEIGHT) - 1) << (c * HEIGHT1) for c in range(WIDTH)]
BOTTOM_MASKS = [1 << (c * HEIGHT1) for c in range(WIDTH)]
TOP_MASKS = [1 << (HEIGHT - 1 + c * HEIGHT1) for c in range(WIDTH)]

MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]  # favor center columns first


def has_won(bits: int) -> bool:
    """Check if a bitboard has a connect-four using shifted masks."""
    # Vertical
    m = bits & (bits >> 1)
    if m & (m >> 2):
        return True
    # Horizontal
    m = bits & (bits >> HEIGHT1)
    if m & (m >> 2 * HEIGHT1):
        return True
    # Diagonal /
    m = bits & (bits >> (HEIGHT1 - 1))
    if m & (m >> 2 * (HEIGHT1 - 1)):
        return True
    # Diagonal \
    m = bits & (bits >> (HEIGHT1 + 1))
    if m & (m >> 2 * (HEIGHT1 + 1)):
        return True
    return False


def make_move(player_bits: int, opponent_bits: int, col: int) -> Tuple[int, int]:
    """Play a move for the current player in the given column using bitboards."""
    mask = player_bits | opponent_bits
    move = (mask + BOTTOM_MASKS[col]) & COLUMN_MASKS[col]
    if move == 0:
        raise ValueError("Column is full")
    player_bits |= move
    return player_bits, opponent_bits


def valid_columns(player_bits: int, opponent_bits: int) -> List[int]:
    """Return playable columns ordered to favor center-first pruning."""
    mask = player_bits | opponent_bits
    return [c for c in MOVE_ORDER if (mask & TOP_MASKS[c]) == 0]


def bit_at(bits: int, row: int, col: int) -> int:
    """Return 1 if the bit at (row, col) is set."""
    idx = col * HEIGHT1 + row
    return (bits >> idx) & 1


def heuristic(ai_bits: int, human_bits: int) -> int:
    """Score the board from the AI's perspective.

    Rewards center control, completed/connectable lines for the AI, and penalizes
    near-term human threats. Magnitudes are coarse to keep evaluation cheap.
    """
    score = 0

    def score_window(window: List[int]) -> None:
        nonlocal score
        ai_count = window.count(1)
        human_count = window.count(-1)
        empty_count = window.count(0)
        if ai_count == 4:
            score += 100000
        elif ai_count == 3 and empty_count == 1:
            score += 100
        elif ai_count == 2 and empty_count == 2:
            score += 10

        if human_count == 3 and empty_count == 1:
            score -= 120  # block threats slightly stronger
        elif human_count == 4:
            score -= 100000

    # Center preference
    center_col = WIDTH // 2
    center_cells = [bit_at(ai_bits, r, center_col) - bit_at(human_bits, r, center_col) for r in range(HEIGHT)]
    score += sum(center_cells) * 6

    # Build grid values: 1 for AI, -1 for human, 0 empty
    grid = [[bit_at(ai_bits, r, c) - bit_at(human_bits, r, c) for c in range(WIDTH)] for r in range(HEIGHT)]

    # Horizontal
    for r in range(HEIGHT):
        for c in range(WIDTH - 3):
            score_window(grid[r][c:c + 4])

    # Vertical
    for c in range(WIDTH):
        for r in range(HEIGHT - 3):
            window = [grid[r + i][c] for i in range(4)]
            score_window(window)

    # Diagonal \
    for r in range(HEIGHT - 3):
        for c in range(WIDTH - 3):
            window = [grid[r + i][c + i] for i in range(4)]
            score_window(window)

    # Diagonal /
    for r in range(HEIGHT - 3):
        for c in range(3, WIDTH):
            window = [grid[r + i][c - i] for i in range(4)]
            score_window(window)

    return score


TTEntry = Tuple[int, int]  # depth, score


def negamax(ai_bits: int, human_bits: int, depth: int, alpha: int, beta: int,
            transposition: Dict[Tuple[int, int], TTEntry]) -> int:
    """Negamax with alpha-beta pruning and a depth-aware transposition table."""
    key = (ai_bits, human_bits)
    if key in transposition:
        stored_depth, stored_score = transposition[key]
        if stored_depth >= depth:
            return stored_score

    if has_won(ai_bits):
        return 1_000_000 + depth  # quicker wins preferred
    if has_won(human_bits):
        return -1_000_000 - depth

    moves = valid_columns(ai_bits, human_bits)
    if depth == 0 or not moves:
        return heuristic(ai_bits, human_bits)

    best = -math.inf
    for col in moves:
        new_ai, new_human = make_move(ai_bits, human_bits, col)
        score = -negamax(new_human, new_ai, depth - 1, -beta, -alpha, transposition)
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    transposition[key] = (depth, best)
    return best


@dataclass
class GameState:
    """Mutable game state wrapper with helper methods for play/search."""
    ai_bits: int = 0
    human_bits: int = 0
    last_human: Optional[Tuple[int, int]] = None  # (row, col)
    last_ai: Optional[Tuple[int, int]] = None     # (row, col)

    def is_full(self) -> bool:
        return all((self.ai_bits | self.human_bits) & TOP_MASKS[c] for c in range(WIDTH))

    def winner(self) -> Optional[str]:
        if has_won(self.human_bits):
            return "human"
        if has_won(self.ai_bits):
            return "computer"
        if self.is_full():
            return "tie"
        return None

    def drop(self, col: int, is_human: bool) -> None:
        if (self.ai_bits | self.human_bits) & TOP_MASKS[col]:
            raise ValueError("Column full")
        # Compute the target row before updating bits so we can store it.
        row = next(r for r in range(HEIGHT) if bit_at(self.ai_bits | self.human_bits, r, col) == 0)
        if is_human:
            self.human_bits, self.ai_bits = make_move(self.human_bits, self.ai_bits, col)
            self.last_human = (row, col)
        else:
            self.ai_bits, self.human_bits = make_move(self.ai_bits, self.human_bits, col)
            self.last_ai = (row, col)

    def available_cols(self) -> List[int]:
        return valid_columns(self.ai_bits, self.human_bits)

    def best_ai_move(self, depth: int) -> int:
        # Randomize first move to avoid deterministic openings and widen variety.
        if self.ai_bits == 0 and self.human_bits == 0:
            open_cols = self.available_cols()
            return random.choice(open_cols)

        transposition: Dict[Tuple[int, int], TTEntry] = {}
        best_score = -math.inf
        best_cols: List[int] = []
        for col in self.available_cols():
            new_ai, new_human = make_move(self.ai_bits, self.human_bits, col)
            score = -negamax(new_human, new_ai, depth - 1, -1_000_000_000, 1_000_000_000, transposition)
            if score > best_score:
                best_score = score
                best_cols = [col]
            elif score == best_score:
                best_cols.append(col)
        return random.choice(best_cols)

    def render(self) -> None:
        symbols = []
        for r in reversed(range(HEIGHT)):
            row_syms = []
            for c in range(WIDTH):
                bit_ai = bit_at(self.ai_bits, r, c)
                bit_hu = bit_at(self.human_bits, r, c)
                sym = "."
                if bit_ai:
                    if self.last_ai == (r, c):
                        sym = "\033[1;93mY\033[0m"
                    else:
                        sym = "\033[93mY\033[0m"
                elif bit_hu:
                    if self.last_human == (r, c):
                        sym = "\033[1;91mR\033[0m"
                    else:
                        sym = "\033[91mR\033[0m"
                row_syms.append(sym)
            symbols.append(" ".join(row_syms))
        print("\n".join(symbols))
        print("0 1 2 3 4 5 6")


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Connect Four against a fast minimax AI.")
    parser.add_argument("-d", "--depth", type=int, default=7, help="Search depth (plies), default 7.")
    turn_group = parser.add_mutually_exclusive_group()
    turn_group.add_argument("-H", "--human-first", action="store_true", help="Force human to start.")
    turn_group.add_argument("-C", "--computer-first", action="store_true", help="Force computer to start.")
    args = parser.parse_args()

    state = GameState()
    human_turn: Optional[bool] = None
    if args.human_first:
        human_turn = True
    elif args.computer_first:
        human_turn = False
    else:
        human_turn = random.random() < 0.5

    print("You are R. Computer is Y.")
    state.render()

    while True:
        if human_turn:
            col_str = input("Enter column (0-6) or q to quit: ").strip()
            if col_str.lower() == "q":
                return
            try:
                col = int(col_str)
            except ValueError:
                continue
            if col < 0 or col >= WIDTH or col not in state.available_cols():
                continue
            state.drop(col, is_human=True)
        else:
            print("Computer thinking...")
            ai_col = state.best_ai_move(depth=args.depth)
            state.drop(ai_col, is_human=False)

        state.render()
        result = state.winner()
        if result == "tie":
            print("Tie.")
            return
        if result == "human":
            print("You win!")
            return
        if result == "computer":
            print("Computer wins!")
            return

        human_turn = not human_turn


if __name__ == "__main__":
    main()
