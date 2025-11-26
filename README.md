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

## Four in a Row
- Play: `python four_in_a_row.py [--human-first] [--max-depth N]`
- Turn order: default random; use `--human-first` to force human start.
- Search: `--max-depth` caps minimax depth (default 3).
- Board: human moves in red; latest computer move highlighted yellow.
