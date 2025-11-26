Games implemented with a shared minimax engine.

## Requirements
- Python 3.9+
- numpy (install via `pip install -r requirements.txt` or `pip install numpy`)

## Tic Tac Toe
- Play: `python tic_tac_toe.py [-d {1,2,3}] [--human-first] [--max-depth N]`
- Difficulty: `-d 1` random, `-d 2` mixed, `-d 3` optimal.
- Turn order: default random; use `--human-first` to force human start.
- Search: `--max-depth` caps minimax depth (default 3).
- Board: human moves shown in red; latest computer move highlighted yellow.

## Connect Four
- Play: `python connect_four.py [--human-first] [--max-depth N]`
- Turn order: default random; use `--human-first` to force human start.
- Search: `--max-depth` caps minimax depth (default 3).
- Board: human moves in red; latest computer move highlighted yellow.

## Future Works
- Gomoku (five-in-a-row) on a small board: same grid logic, just change the win-length and add a heuristic + depth limit for larger boards.
- Reversi/Othello: manageable branching with alpha–beta; you’d add a flanking/capture move generator and a disk-difference/positional heuristic.
- Checkers (small variant): larger branching, but still feasible with a tighter depth cap and a piece-count/king-weighted heuristic.
- Quarto (4×4): low branching; each move both places a piece and hands a piece to the opponent—minimax handles the dual-choice turn structure well.   
