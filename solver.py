from typing import Tuple, List
import numpy as np
import cvxpy as cp
from constants import *
from board import Board


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
    last_solution : List[List[float]]
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
