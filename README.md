# Minesweeper

In this project you are going to use Linear Programming iteratively to solve a game of Minesweeper. Define a variable $x[i, j]$ which holds the probability that block $(i, j)$ contains a mine. Every $x[i, j]$ is in $[0, 1]$ and the total number of mines should be the same as the total on the board. Finally, for each revealed block, two constraints are required: The revealed block has zero probability of containing a mine and the mines of the eight neighbors are in total the equal to the number revealed.

Use this starter code and fill in all the TODOs.

## Required packages

Use the following command to install the required packages.

```bash
python -m pip install -r requirements.txt
```

## Example usage

Review the programs usage here:

```
python game.py -h                         
pygame 2.2.0 (SDL 2.0.22, Python 3.7.6)
Hello from the pygame community. https://www.pygame.org/contribute.html
usage: Minesweeper Solver [-h] [--rows ROWS] [--columns COLUMNS]
                          [--mines MINES] [--seed SEED] [--no-render]
                          [--block-size BLOCK_SIZE] [--verbose]

You will be using Linear Programming iteratively to progressively solve a
minesweeper board

optional arguments:
  -h, --help            show this help message and exit
  --rows ROWS, -r ROWS  Board rows
  --columns COLUMNS, -c COLUMNS
                        Board columns
  --mines MINES, -m MINES
                        Number of mines on the board
  --seed SEED, -s SEED  Provide a seed to recreate the same boards.
  --no-render           Disable rendering for testing purposes
  --block-size BLOCK_SIZE, -b BLOCK_SIZE
                        Size of each block in pixels
  --verbose, -v         Increase verbosity

University of Chicago, CMSC 27200 Spring '23 Konstantinos Ameranis, Lorenzo
Orecchia, Ivan Galakhov
```

When you are done with coding your solution, you can use your solver in the following way `python game.py -b 40 -v -r 24 -c 30 -m 150`
