"""Minesweeper

This program uses Linear Programming to solve the classic game of minesweeper.
Through the use of pygame the game state can be visualized.
With minimal changes it can become a functional minesweeper game with mouse controls.

The three classes are `Board` which stores the state and is responsible for drawing anything game related.
The `MinesweeperLPSolver` class is responsible for computing a set of points to click and/or flag in each iteration.
Finally, `Game` handles the communication between the two and incorporates the main loop of the game, including user controls.

University of Chicago
CMSC 27200, Theory of Algorithms
Spring 2023
Konstantinos Ameranis
"""

from random import sample
import argparse
import time
from typing import Tuple, List
import pygame
from pygame.locals import *
import numpy as np
import cvxpy as cp


EPSILON = 1e-2
ROWS = 24
COLUMNS = 30
MINES = 150
BLOCK_SIZE = 40


class Board:
    """Board

    This object holds the state of minesweeper, including which blockss have been clicked, flagged and/or contain a mine.
    Also responsible for drawing itself on the pygame.Surface.surface provided by the game.

    Attributes
    ----------
    windowWidth : int
        Number of columns in the board.
    windowHeight : int
        Number of rows in the board.
    blockSize : int
        Side length of each block in pixels.
    pressed : List[List[bool]]
        Whether sqaure (i, j) has been pressed.
    flagged ; List[List[bool]]
        whether block (i, j) is flagged.
    mines : int
        Number of mines present in the board.
    render : bool
        Whehter the board is rendered. Mostly used for testing and when running on a system with no graphical environment.
    verbose : int
        How much the object is printing about the operations it's taking.
    neighboring_mine_count ; List[List[int]]
        How many mines there are adjacent to block (i, j).
    colors : List[Tuple[str, Tuple[int, int, int]]]
        Assigned colors to different mine count. Similar to original game.
    flag_image : pygame.Surface.surface
        Image used for rendering a flagged block.
    bomb_image : pygame.Surface.surface
        Image used for rendering a revealed bomb after loss.
    _bombed : bool
        Whether a bomb was clicked on the current board.
    remaining : int
        How many non bomb blockss are left unclicked.
    self.flags_remaining : int
        How many mines there are, minus the number of flagged blocks on the board.
    """
    def __init__(self, windowWidth: int = COLUMNS, windowHeight: int = ROWS, blockSize: int = BLOCK_SIZE, mines: int = MINES, render: bool = True, verbose: int = 0) -> None:
        """Initialize the Board with rows, columns, mines, block size, whether the board is rendered and verbosity"""
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.blockSize = blockSize
        self.pressed: List[List[bool]]
        self.flagged: List[List[bool]]
        self.mines = mines
        self.render = render
        self.verbose = verbose
        self.is_mine: List[List[bool]]
        self.neighboring_mine_count: List[List[int]]
        self.colors = [
            ("White", (192, 192, 192)),
            ("Blue", (0, 0, 255)),
            ("Green", (0, 255, 0)),
            ("Red", (255, 0, 0)),
            ("Purple", (255, 0, 255)),
            ("Black", (64, 64, 64)),
            ("Maroon", (128, 0, 0)),
            ("Gray", (128, 128, 128)),
            ("Turquoise", (64, 224, 208))
        ]
        self.font = None
        self.flag_image = None
        self.mine_image = None
        self._bombed = False
        self.remaining = self.windowWidth * self.windowHeight - self.mines
        self.flags_remaining = self.mines

    def create(self) -> None:
        """Create a new board

        Selects `mines` blocks at random and computes the necessary auxiliary variables.

        Parameters
        ----------

        Returns
        -------
        """
        # Reset variables
        self.pressed = [[False] * self.windowWidth for _ in range(self.windowHeight)]
        self.flagged = [[False] * self.windowWidth for _ in range(self.windowHeight)]
        self.is_mine = [[False] * self.windowWidth for _ in range(self.windowHeight)]
        self.neighboring_mine_count = [[0] * self.windowWidth for _ in range(self.windowHeight)]
        self.remaining = self.windowWidth * self.windowHeight - self.mines
        self.flags_remaining = self.mines
        self._bombed = False

        if self.render:
            self.font = pygame.font.SysFont("Times New Roman", 30)

        # Select mined blocks
        candidates = sum([[(x, y) for x in range(self.windowWidth)] for y in range(self.windowHeight)], [])
        mines = sample(candidates, self.mines)
        for x, y in mines:
            self.is_mine[y][x] = True

        # Compute auxiliary variables
        for x in range(self.windowWidth):
            for y in range(self.windowHeight):
                if self.is_mine[y][x]:
                    for new_x, new_y in [(x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y), (x-1, y-1), (x, y-1), (x+1, y-1)]:
                        if (0 <= new_x < self.windowWidth) and (0 <= new_y < self.windowHeight):
                            self.neighboring_mine_count[new_y][new_x] = self.neighboring_mine_count[new_y][new_x] + 1
        if self.verbose > 0:
            print(f'Successfully created new board {self.windowHeight}x{self.windowWidth} with {self.mines} mines.')

    def draw(self, surface: pygame.surface.Surface) -> None:
        """Draw board

        For each block, draw what is needed, number, flag or bomb.
        Finally draw the grid

        Parameters
        ----------
        surface : pygame.Surface.surface
            The surface to draw on.

        Returns
        -------
        """
        if not self.render:
            return
        for x in range(self.windowWidth):
            for y in range(self.windowHeight):
                if self.pressed[y][x]:
                    pygame.draw.rect(surface, self.colors[0][1], (x * self.blockSize, y * self.blockSize, self.blockSize, self.blockSize))
                    if self.neighboring_mine_count[y][x] > 0:
                        text = self.font.render(str(self.neighboring_mine_count[y][x]), True, self.colors[self.neighboring_mine_count[y][x]][1])
                        textRect = text.get_rect()
                        textRect.center = ((x + 0.5) * self.blockSize, (y + 0.5) * self.blockSize)
                        surface.blit(text, textRect)
                if self.flagged[y][x] and not self._bombed:
                    if self.flag_image is None:
                        self.flag_image = pygame.image.load("flag.png").convert()
                        self.flag_image = pygame.transform.scale(self.flag_image, (self.blockSize, self.blockSize))
                    surface.blit(self.flag_image, (x * self.blockSize, y * self.blockSize))
                if self.is_mine[y][x] and self._bombed:
                    if self.mine_image is None:
                        self.mine_image = pygame.image.load("mine.jpg").convert()
                        self.mine_image = pygame.transform.scale(self.mine_image, (self.blockSize, self.blockSize))
                    surface.blit(self.mine_image, (x * self.blockSize, y * self.blockSize))
        for x in range(self.windowWidth):
            pygame.draw.rect(surface, (255, 255, 255), ((x + 1) * self.blockSize, 0, 2, self.windowHeight * self.blockSize))
        for y in range(self.windowHeight):
            pygame.draw.rect(surface, (255, 255, 255), (0, (y + 1) * self.blockSize, self.windowWidth * self.blockSize, 2))

    def click(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Click on block (x, y)

        Take care of revealing all necessary blocks and return them in a list

        Parameters
        ----------
        x : int
            Which column the block is in.
        y : int
            Which row the block is in.

        Returns
        -------
        revealed : List[Tuple[int, int]]
            All the points that are revealed by clicking on (x, y)
        """
        if self.verbose > 2:
            print("Clicked", x, y)
        if self._bombed or self.pressed[y][x] or self.flagged[y][x]:
            return []
        if self.is_mine[y][x]:
            self._bombed = True
            if self.verbose > 0:
                print("You goofed")
            return [(x, y, -1)]
        self.pressed[y][x] = True
        self.remaining = self.remaining - 1
        revealed = [(x, y, self.neighboring_mine_count[y][x])]

        # If there are no neighboring mines recurse on all neighbors
        if self.neighboring_mine_count[y][x] == 0:
            for new_x, new_y in [(x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y), (x-1, y-1), (x, y-1), (x+1, y-1)]:
                if (0 <= new_x < self.windowWidth) and (0 <= new_y < self.windowHeight):
                    revealed.extend(self.click(new_x, new_y))
        return revealed

    def flag(self, x: int, y: int) -> None:
        """Flag block (x, y)

        Informs the board that block (x, y) is flagged.

        Parameters
        ----------
        x : int
            Which column the block is in.
        y : int
            Which row the block is in.

        Returns
        -------
        """
        if self._bombed or self.pressed[y][x]:
            return
        self.flagged[y][x] = not self.flagged[y][x]
        self.flags_remaining += 1 if not self.flagged[y][x] else -1


    def has_won(self) -> int:
        """Whether the board is won

        Parameters
        ----------

        Returns
        -------
        won : bool
            Whether all non mined blocks have been clicked.
        """
        return self.remaining == 0


class MinesweeperLPSolver():
    """Solving Minesweeper using LP

    Use Linear Programming to solve minesweeper interactively

    Attributes
    ---------
    board : Board
        The board the solver is going to try to solve.
    verbose : int
        Controls the verbosity.
    x : cp.Variable
        Variables that go into the cvxpy problem. A value of one means that block (x, y) is a mine.
    constraints : List[cvxpy.constraints.constraint.Constraint]
        Linear Program constraints to be used for iterative solving.
    objective : cvxpy.problems.objective.Objective
        Zero objective that needs to be provided to the Linear Problem.
    last_solution : numpy.ndarray
        Solution values from previous iteration, can be used to speed up computation of new solution.
    known : numpy.ndarray
        Number of mines in each revealed square or -1.
    clicked : set
        Which blocks have been clicked.
    flagged : set
        Which blocks have been flagged.
    prob : cvxpy.Problem
        CVXPY problem that is iteratively used.
    """
    def __init__(self, board: Board, verbose: int = 0) -> None:
        self.board = board
        self.verbose = verbose
        # TODO: Define the LP variables, objective and anything else you need
        self.x: cp.Variable                                             # TODO: Define your variables
        self.constraints: List[cp.constraints.constraint.Constraint]    # TODO: Initialize constraints
        self.objective: cp.problems.objective.Objective                 # TODO: Initialize with an objective
        self.last_solution: np.ndarray                                  # TODO: Initialize to mines / blocks
        self.known = - np.ones(((self.board.windowHeight, self.board.windowWidth)))
        self.clicked = set()
        self.flagged = set()
        self.prob: cp.Problem

    def get_next(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Returns the coordinates of the next blocks to click or flag

        Construct the problem, solve it, use the solution to decide on what blocks to click.

        Parameters
        ----------

        Returns
        -------
        zero_pos : List[Tuple[int, int]
            Blocks with the smallest probability to contain a mine that haven't been clicked yet.
        one_pos : List[Tuple[int, int]
            Blocks with probability close to enough to one that have not been flagged.
        """
        # TODO: Create and solve the problem

        # TODO: Retrieve the solution and find which blocks are close enough to one
        # and which close enough to zero; or the unclicked one with lowest value.
        return [], []

    def add_constraint(self, i: int, j: int, mine_count: int) -> None:
        """Add a constraint based on the value of block (i, j)

        Parameters
        ----------
        i : int
            Which column the block is in.
        j : int
            Which row the block is in.
        mine_count : int
            How many mines there are in the block (i, j).

        Returns
        -------
        """
        if self.verbose > 2:
            print("Adding", i, j, mine_count)
        # TODO: Add a constraint for this block and its neighbors


class Game:
    """Game

    The game module is responsible for running the game.

    Attributes
    ----------
    windowWidth : int
        Number of columns in the board.
    windowHeight : int
        Number of rows in the board.
    blockSize : int
        Size of eachblock in pixels.
    board : Board
        Board object that stores all the minesweeper information.
    mines : int
        Number of mines on the board.
    render : bool
        Whether to render the board on the screen. Set to False for testing and when running in an environment with no graphical environment.
    verbose : int
        Level of verbosity.
    time : float
        Timestamp the current game started.
    win_time : float
        Time it has taken to end the game, win or lose.
    solver : MinesweperLPSolver
        Solver used to uncover the solution to the game.
    """
    def __init__(self, windowWidth: int = COLUMNS, windowHeight: int = ROWS, blockSize: int = BLOCK_SIZE, mines: int = MINES, render: bool = True, verbose: int = 0) -> None:
        """This is the initializing function of the Game object"""
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.blockSize = blockSize
        self.board = Board(self.windowWidth, self.windowHeight, self.blockSize, mines, render, verbose)
        self.render = render
        self.verbose = verbose
        self.time: float = 0
        self.win_time: float = 0
        self.font = None
        self._running = False
        self._display_surf: pygame.Surface
        self.solver: MinesweeperLPSolver
        self.loop_count = 0

    def on_init(self) -> None:
        """Start a new game

        Have the board create a new instance and create a new solver object.

        Parameters
        ----------

        Returns
        -------
        """
        self._running = False
        if self.render:
            pygame.init()
            self._display_surf = pygame.display.set_mode((self.windowWidth * self.blockSize, self.windowHeight * self.blockSize + 80), pygame.HWSURFACE)
            pygame.display.set_caption('UChicago TheoryWorld Minesweeper')
            self.font = pygame.font.SysFont("Times New Roman", 40)
        self.board.create()
        self.solver = MinesweeperLPSolver(self.board, verbose=self.verbose)
        self.time = time.time()
        self.win_time = 0
        self.loop_count = 0

        self._running = True

    def on_loop(self) -> None:
        """Actions taken every round

        Parameters
        ----------

        Returns
        -------
        """
        if self.board._bombed:
            self._running = False
            self.win_time = time.time()
            return
        click, flag = self.solver.get_next()
        for x, y in click:
            revealed_squares = self.board.click(x, y)
            for i, j, mine_count in revealed_squares:
                self.solver.add_constraint(i, j, mine_count)

        for x, y in flag:
            if self.verbose > 1:
                print("Flagging", x, y)
            self.board.flag(x, y)

        self.loop_count += 1
        if self.verbose > 0:
            progress_percent = 1 - self.board.remaining / (self.windowHeight * self.windowWidth - self.board.mines)
            progress_bar = '▉' * int(progress_percent * 40)
            print(f'Loop Count {self.loop_count:3d}: Blocks remaining = {self.board.remaining:4d} [{progress_bar:40s}]')

    def on_render(self) -> None:
        """Render the board in pygame

        Reset the surface, have the board render itself, print the extra information.

        Parameters
        ----------

        Returns
        -------
        """
        if not self.render:
            return
        self._display_surf.fill((0, 128, 255))
        self.board.draw(self._display_surf)
        if self._running:
            time_text = self.font.render(f'{time.time() - self.time:.0f}s', False, (255, 255, 255))
        else:
            time_text = self.font.render(f'{self.win_time - self.time:.0f}s', False, (255, 255, 255))
        self._display_surf.blit(time_text, (80, self.windowHeight * self.blockSize + 10))
        remaining_text = self.font.render(str(self.board.flags_remaining), False, (255, 255, 255))
        self._display_surf.blit(remaining_text, (self.windowWidth * self.blockSize - 80, self.windowHeight * self.blockSize + 10))
        pygame.display.flip()

    def win(self) -> None:
        """Win! Congratulations

        Stop the game and congratulate.

        Parameters
        ----------

        Returns
        -------
        """
        self.win_time = time.time()
        if self.render:
            self.on_render()
            text = pygame.font.SysFont('Times New Roman', 100)
            text_surf = text.render("Y O U   W I N !", True, (255, 0, 0), (0, 128, 255))
            textRect = text_surf.get_rect()
            textRect.center = (self.windowWidth * self.blockSize // 2, self.windowHeight * self.blockSize // 2)
            self._display_surf.blit(text_surf, textRect)
            pygame.display.flip()
        self._running = False

    def quit(self) -> None:
        """End the Game

        Performs cleanup.

        Parameters
        ----------

        Returns
        -------
        """
        if self.render:
            pygame.quit()

    def on_execute(self) -> bool:
        """Main loop of the game

        Receive input for control, get next solutions and render.

        Parameters
        ----------

        Returns
        -------
        won : bool
            Whether the last board was won.
        """
        self.on_init()

        while True:
            if self.render:
                pygame.event.pump()
                keys = pygame.key.get_pressed()

            if self._running:
                # If you fiddle with this comment you can turn this code into a 1-player minesweeper game.
                #events = pygame.event.get()
                #for event in events:
                #    if event.type == pygame.MOUSEBUTTONUP:
                #        x, y = pygame.mouse.get_pos()
                #        x, y = x // self.blockSize, y // self.blockSize
                #        if event.button == 1 and (x < self.windowWidth) and (y < self.windowHeight):       # Left click
                #            self.board.click(x, y)
                #        if event.button == 3:       # right click
                #            self.board.flag(x, y)
                if self.render:
                    self.on_render()
                self.on_loop()


                if self.board.has_won():
                    self.win()
            if self.render:
                if keys[K_SPACE]:
                    self.on_init()

                if keys[K_ESCAPE]:
                    self.quit()
                    return self.board.has_won()
            if not self.render and not self._running:
                return self.board.has_won()
            # time.sleep(1 / 50)
        self.quit()
        return self.board.has_won()


def parse_args() -> argparse.Namespace:
    """Parse arguments

    Use the `-h` option to list available command line arguments
    """
    parser = argparse.ArgumentParser(prog='Minesweeper Solver',
                                     description='You will be using Linear Programming iteratively to progressively solve a minesweeper board',
                                     epilog='University of Chicago, CMSC 27200 Spring \'23 Konstantinos Ameranis, Lorenzo Orecchia')
    parser.add_argument('--rows', '-r', type=int, default=ROWS, help='Board rows')
    parser.add_argument('--columns', '-c', type=int, default=COLUMNS, help='Board columns')
    parser.add_argument('--mines', '-m', type=int, default=MINES, help='Number of mines on the board')
    parser.add_argument('--no-render', action='store_true', help='Disable rendering for testing purposes')
    parser.add_argument('--block-size', '-b', type=int, default=BLOCK_SIZE, help='Size of each block in pixels')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase verbosity')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    game = Game(windowWidth=args.columns, windowHeight=args.rows, blockSize=args.block_size, mines=args.mines, render=not args.no_render, verbose=args.verbose)
    game.on_execute()
