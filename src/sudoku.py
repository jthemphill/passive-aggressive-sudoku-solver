#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
# Jeffrey Hemphill
#
# January 15, 2012

"""Sudoku solver for Python 2.7, optimized as a CGI script.

Implements Donald Knuth's Algorithm X via the Dancing Links method in
order to produce all possible solutions from a given Sudoku
puzzle. For a complete explanation of the method, see
arXiv:cs/0011047.

This module can only handle n-values between 1 and 35; said limitation
stems from the add_filled_cell function.

--------------------------- A note on terminology -----------------------------

Throughout the comments, the variable n is referenced with no
explanation.  n is the number of rows, columns, boxes, and digits
within the Sudoku puzzle being solved. The most common value for n is
9, though a fair number of puzzles use an n-value of 12.

When the words 'row,' 'column,' 'cell,' and 'box' are used, the
program is always referring to the original Sudoku
puzzle. Two-dimensional matrices such as the SudokuMatrix object also
have rows and columns, but these are referred to as 'Candidates' and
'Constraints' in order to avoid ambiguity.

The variables 'digit' and 'num' both refer to a value in a Sudoku
cell. The only difference is that digit lies on the xrange [1, n + 1)
and num lies on the xrange [0, n). digit is used exclusively for input
and output. Everywhere else, num should be used.

------------------------------- doctest example -------------------------------

>>> find_solutions('\
530070000\
600195000\
098000060\
800060003\
400803001\
700020006\
060000280\
000419005\
000080079', n=9, boxWidth=3)
'\
534678912\
672195348\
198342567\
859761423\
426853791\
713924856\
961537284\
287419635\
345286179\
'

>>> find_solutions(_EMPTY_GRID) == '0'*81
True

"""

_DIGITS = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Default arguments for a standard 9 x 9 Sudoku grid.
_N = 9
_BOX_WIDTH = 3
_EMPTY_GRID = "0"*_N**2


# Number of solutions to find before halting. For an interactive
# application, two is all we need to determine if we have arrived at a
# unique solution.
_NUMSOLS = 2

# Uncomment if you want to find all solutions.
# _NUMSOLS = float('inf')

def find_solutions(L, n=9, boxWidth=3, numSols=_NUMSOLS):
    """Solve an n by n Sudoku grid represented by the list or string L.

    In its current form, find_solutions(L) will simply print all
    solutions, without storing or passing these solutions to another
    program.

    Keyword arguments:

    n: the number of rows, columns, boxes, and digits in the grid.

    boxWidth: the number of columns which each box spans.

    L: a list of length n**2 consisting of digits 0 through n, where 0
    denotes an empty cell.

    numSols: the number of solutions to find before halting. Use
    float('inf') if you want to find all solutions.

    """
    solver = SudokuMatrix(L, n, boxWidth, numSols)
    solutions = solver.solve()
    
    # Print solution if unique.
    if solutions[1:] == []:
        return solutions[0]

    # If no unique solution, return original grid.
    else:
        return solver.original_grid

class SudokuMatrix:
    """A sparse matrix representing a Sudoku grid.

    The SudokuMatrix is represented by two circular doubly-linked lists.

    The list of Candidates runs vertically. Each Candidate represents the act
    of inputting a value into a cell.

    The list of Constraints runs horizontally. Each Constraint represents a
    rule of Sudoku.

    A Node exists at the intersection of every Candidate and Constraint. Nodes
    link and unlink themselves from the Candidates and Constraints in order to
    add and remove themselves from the SudokuMatrix.

    The exact cover problem, and hence the Sudoku puzzle, is solved when the
    matrix has chosen Candidates such that each Constraint has exactly one Node
    underneath it.

    """
    def __init__(self, original_grid=_EMPTY_GRID,
                 n=_N, boxWidth=_BOX_WIDTH, numSols=_NUMSOLS):
        """Create a SudokuMatrix representing an n x n Sudoku grid.

        Keyword Arguments:

        original_grid: A list or string of n**2 integers between 0 and
        n, going left to right then top to bottom. 0 denotes an empty
        cell.

        n: the number of rows, columns, boxes, and different numbers
        in the grid. The majority of Sudoku grids choose n =
        9. Currently, n is limited to the xrange [1,36).

        boxWidth: the horizontal width of each box in the grid. If n
        does not equal 9, a boxWidth must be specified. The majority
        of Sudoku grids choose boxWidth = 3.

        numSols: the number of solutions to find before halting.

        """
        assert(1 < n < 35)
        assert(n % boxWidth == 0)

        self.n = n

        # boxWidth is the number of cells horizontally spanning the
        # box.
        self.boxWidth = boxWidth
        
        # Backup the original grid.
        self.original_grid = original_grid

        # boxHeight is both the height of each box and the number of
        # boxes per row.
        self.boxHeight = self.n // boxWidth

        self.numSols = numSols

        self.initialize_matrix()

        self.set_grid(original_grid)

    def initialize_matrix(self):
        """Initialize the data structures of the SudokuMatrix."""
        # We need n**3 Candidates.
        self.candidates = []

        # We need 4 * n**2 Constraints, with a root linking into them.
        self.root = Root(self.n)


        # The four rules of Sudoku inform our constraints:

        # One number per cell.
        self.celConstraints = []

        # One of each digit per row.
        self.rowConstraints = []

        # One of each digit per column.
        self.colConstraints = []

        # One of each digit per box.
        self.boxConstraints = []


        # A list containing the Candidates which have so far been chosen.
        self.choices = []

        for i in xrange(self.n):
            for j in xrange(self.n):

                self.celConstraints.append(Constraint(self))
                self.rowConstraints.append(Constraint(self))
                self.colConstraints.append(Constraint(self))
                self.boxConstraints.append(Constraint(self))

        for row in xrange(self.n):
            for col in xrange(self.n):
                # The box in which the given cell falls
                box = (col // self.boxWidth +
                       self.boxHeight * (row // self.boxHeight))

                # Generate a Candidate for each cell / number combination.
                for num in xrange(self.n):
                    self.candidates.append(Candidate(self, row, col, box, num))

    def __str__(self):
        """Represent the partial solution as a two-dimensional Sudoku grid."""
        n = self.n
        gridString = self.get_string()
        return pretty_print(gridString)
    
    def __repr__(self):
        """String representation of the current SudokuMatrix."""
        return ("SudokuMatrix(original_grid='%s', n=%d, boxWidth=%d)" %
                (self.get_string(), self.n, self.boxWidth))

    def get_string(self):
        """Represent the partial solution as a string of n**2 characters."""
        choices = sorted(self.choices)

        s = ""
        loc = 0                        # Number of current cell being displayed
        candidate = 0                     # Number of next Candidate to display
        numCandidates = len(choices)
        
        for row in xrange(self.n):
            for col in xrange(self.n):

                # solution[candidate][0] is the number of the next solved cell.
                if  ( (candidate < numCandidates) and
                      (loc == choices[candidate][0]) ):
                    s += _DIGITS[choices[candidate][1].num]
                    candidate += 1
                else:
                    s += "0"

                loc += 1
        return s

    def set_grid(self, s):
        """Adds the filled cells provided by the Sudoku puzzle.

        s must be a string or list of length n**2 composed of integers
        between 0 and n.

        Each element of s corresponds to a cell in the Sudoku grid,
        going left to right then top to bottom. 0 denotes an empty cell.

        """
        assert(len(s) == self.n**2)

        # reset the matrix if its grid has been set already.
        while self.choices != []:
            self.backtrack()

        for row in xrange(self.n):
            for col in xrange(self.n):
                digit = s[row * self.n + col]
                try:
                    self.add_filled_cell(row, col, digit)
                except CellViolation as e:
                    print e

    def add_filled_cell(self, row, col, digit):
        """Add a filled cell to the calling SudokuMatrix's solution.

        Handles string and integer inputs well enough for most Sudoku
        puzzles found in the wild. Assumes all inputs are in base n + 1.
        Since string to integer conversion relies on Python's int function,
        this module only supports n <= 35.

        Keyword Arguments:

        row: the cell's row on the Sudoku grid. Must be in the xrange [0,n).
        col: the cell's column on the Sudoku grid. Must be in the xrange [0,n).
        digit: the digit within the cell. Must be in the xrange [1, n + 1).

        >>> foo = SudokuMatrix()
        >>> foo.add_filled_cell(0,0,3)
        >>> foo.choices[0][1].location
        0
        >>> foo.choices[0][1].num
        2

        """
        if type(digit) == type(str()):
            # give user the benefit of the doubt that digit <= n.
            if len(digit) > 1:
                digit = int(digit)
            else:
                digit = int(digit, self.n + 1)

        # Return if the cell is empty.
        if digit == 0:
            return

        if digit > self.n:
            raise CellViolation(row, col, digit, self.n)

        num = digit - 1

        # Add the represented Candidate to the partial solution.
        x = self.candidates[row * self.n**2 + col * self.n + num]
        x.choose(self)

    def solve(self, solutions=None, depth=0):
        """Solve the puzzle and call self.__solution_found()."""
        
        if solutions == None:
            solutions = []

        # Base Case: backtrack to start if no more solutions are desired.
        if self.numSols <= 0:
            self.backtrack()
            return solutions

        # Success base case: matrix is empty.
        elif self.root.right == self.root:
            return self.__solution_found(solutions)

        else:
            selectedConstraint = self.chosen_constraint()
            
            # Failure base: logical contradiction found.
            if selectedConstraint.size <= 0:
                self.backtrack()
                return solutions

            selectedNode = selectedConstraint.down

            # Try all Candidates intersecting this Constraint.
            while selectedNode != selectedConstraint:

                selectedNode.candidate.choose(self)

                # Recurse to fully explore this branch.
                self.solve(solutions, depth + 1)

                # After the maximum depth has been reached by
                # recursion, try the next Candidate.
                selectedNode = selectedNode.down

            # Every choice below this depth has been made.
            if depth > 0:
                self.backtrack()

            return solutions

    def __solution_found(self, solutions):
        """Print the matrix's state, tack off a solution, and backtrack."""
        self.numSols -= 1

        solutions.append(self.get_string())
        self.backtrack()
        return solutions

    def backtrack(self):
        """Restore the matrix to its previous state."""
        lastChoice = self.choices.pop()[1]
        lastChoice.unchoose()

    def chosen_constraint(self):
        """Return the Constraint with the fewest uncovered nodes."""
        constraint = self.root.right
        size = float('inf')

        while constraint is not self.root:

            if constraint.size < size:
                selectedConstraint = constraint
                size = constraint.size

            constraint = constraint.right

        return selectedConstraint

################################## Root Node ##################################

class Root:
    """The Root is the absolute beginning of the circular matrix."""
    def __init__(self, n):
        """Create a Root."""
        self.up = self
        self.down = self
        self.left = self
        self.right = self

        self.size = n**3                      # Number of Candidates under root

#################################### Nodes ####################################

class Node:
    """Represents a nonzero value in the SudokuMatrix.

    Contains links to the Nodes above it, below it, to its left and right, and
    to its corresponding Candidate and Constraint.

    In addition, contains a boolean declaring its covered or uncovered status.

    """
    def __init__(self, candidate, constraint):
        """Create a Node under the given candidate and constraint."""
        self.candidate = candidate
        self.constraint = constraint

        upNode = self.constraint.up

        self.down = constraint
        constraint.up = self
        self.up = upNode
        upNode.down = self

    def cover_node(self):
        """Remove the calling Node from the matrix.

        Link the Node to the right of the calling Node with the Node on the
        calling Node's left; the same goes for the upper and lower Nodes.

        The adjacent Nodes will then bypass the calling object, rendering the
        calling object unreferenceable from within the matrix.

        Covering a Node will also cover all Nodes
        belonging to the same Candidate.

        """
        # Link the upper Node to the lower Node
        self.up.down = self.down
        self.down.up = self.up

        # Self is no longer a member of the Constraint
        self.constraint.size -= 1

    def uncover_node(self):
        """Invert the cover_node function.

        Link the calling Node and its neighbor back into their rightful place
        in the matrix, such that adjacent Nodes link to the calling Node.

        """
        # Link self to the lower and upper Nodes
        self.down.up = self
        self.up.down = self

        # Self is added back into Constraint
        self.constraint.size += 1

################################# Candidates ##################################

class Candidate(Node):
    """Represents a combination of a cell and a number.

    Each Candidate represents the consequences of placing a certain number
    in a certain cell. There are n numbers and n**2 cells, so, by
    combinatorics, the total number of candidates in a Sudoku grid is their
    product: n**3.

    In the SudokuMatrix, a Candidate is a horizontal linked list of Nodes.

    """
    def __init__(self, A, row, col, box, num):
        """Create a Candidate and its four Nodes.

        Keyword Arguments:
        A: the SudokuMatrix of which the Candidate is a part.
        row: the number of the row in the Sudoku grid.
        col: the number of the column in the Sudoku grid.
        box: the number of the box in the Sudoku grid.
        num: the digit which would be filled in the Candidate's cell, minus 1.

        """
        self.location = row * A.n + col
        self.constraint = A.root

        # Each of these variables is a Constraint corresponding to the node.
        self.cel = A.celConstraints[row * A.n + col]
        self.row = A.rowConstraints[row * A.n + num]
        self.col = A.colConstraints[col * A.n + num]
        self.box = A.boxConstraints[box * A.n + num]

        # Digit inside of Candidate cell is on xrange [1,n]
        self.num = num

        # this tuple contains the Constraints under which Nodes should be
        # formed.
        self.intersections = self.cel, self.row, self.col, self.box

        # Directionally link self into list of Candidates
        prev = A.root.up

        A.root.up = self
        prev.down = self
        self.up = prev
        self.down = A.root

        # Create a Node at the intersection of self and its Constraints
        self.left = self

        for x in self.intersections:
            newNode = Node(self, x)

            leftNode = self.left

            newNode.left = leftNode
            leftNode.right = newNode
            self.left = newNode
            newNode.right = self

    def choose(self, A):
        """Add self to partial solution of A and cover all Nodes under self."""
        A.choices.append((self.location, self))

        # Cover every Constraint intersecting the Candidate.
        x = self.right
        while x != self:
            x.constraint.cover()
            x = x.right

    def unchoose(self):
        """Undo the choose function and remove self from the matrix."""
        for x in reversed(self.intersections):
            x.uncover()

    def legality_check(self):
        """Raises an exception if choosing the Candidate is not legal.

        The choice will not be legal if more than one number is placed in a
        cell or if the same number is placed in a row, column, or box more
        than once.

        """
        if self in A.choices:
            return

        if not self.legal_cell():
            raise CellViolation(self.cel)

        if not self.legal_row():
            raise RowViolation(self.row)

        if not self.legal_column():
            raise ColumnViolation(self.col)

        if not self.legal_box():
            raise BoxViolation(self.box)

    def legal_cell(self):
        """Returns True if the Candidate cell is empty."""
        return not self.cel.covered

    def legal_row(self):
        """Returns True if the Candidate row is legal."""
        return not self.row.covered

    def legal_column(self):
        """Returns True if the Candidate column is legal."""
        return not self.col.covered

    def legal_box(self):
        """Returns True if the Candidate box is legal."""
        return not self.box.covered

################################# Constraints #################################

class Constraint:
    """Represents a Constraint in the SudokuMatrix.

    A Constraint is the header for a column of the SudokuMatrix, corresponding
    to a facet of one of the four rules of Sudoku. Covering a Constraint will
    also cover each of the nodes above and below it, eliminating possibilities
    which no longer exist after inputting a number.

    """

    def __init__(self, sudokuMatrix):
        """Link self to the given sudokuMatrix."""
        # size is the number of nodes under the constraint.
        # size always begins as N, and decrements until it reaches 1.
        # When size = 1, the Constraint is satisfied.
        self.size = sudokuMatrix.n

        prevConstraint = sudokuMatrix.root.left

        prevConstraint.right = self
        self.left = prevConstraint

        self.right = sudokuMatrix.root
        sudokuMatrix.root.left = self

        self.up = self
        self.down = self

        self.covered = False

    def cover(self):
        """Unlink the Constraint from the SudokuMatrix.

        The Constraint itself is unlinked from the Matrix, along with all
        Candidates which intersect the Constraint.

        """
        if not self.covered:
            self.covered = True

            # unlink Constraint from header
            self.left.right = self.right
            self.right.left = self.left

            # Take each Node under the Constraint
            downNode = self.down
            while downNode is not self:
                # and cover each Node to its right and left.
                rightNode = downNode.right
                while rightNode is not downNode:
                    rightNode.cover_node()
                    rightNode = rightNode.right
                downNode = downNode.down

    def uncover(self):
        """Invert the cover(self) function.

        Link the Constraint back into the matrix, uncovering each node that
        was covered by cover(self).

        """
        if self.covered:
            self.covered = False

            # Add Constraint back into header list
            self.right.left = self
            self.left.right = self

            # Replace all candidates previously covered
            upNode = self.up
            while upNode is not self:
                leftNode = upNode.left
                while leftNode is not upNode:
                    leftNode.uncover_node()
                    leftNode = leftNode.left
                upNode = upNode.up

############################## Utility Functions ##############################
                
def pretty_print(gridString):
    """Format the gridString as a Sudoku Grid."""
    from math import sqrt
    n = int(sqrt(len(gridString)))
    s = ""

    for row in xrange(n):
        for col in xrange(n):
            cellValue = gridString[row * n + col]

            if cellValue == "0":
                s += "  "
            else:
                s += "%s " % (cellValue)
        s += "\n"
    return s

################################# Exceptions ##################################

class Error(Exception):
    """Base class for Exceptions in this module."""
    pass

class OutOfXrange(Error):
    """Raised when a cell outside of the Sudoku grid is filled."""
    pass

class RuleViolation(Error):
    """Base class for a violation of the rules of Sudoku."""
    pass

class CellViolation(RuleViolation):
    """Raised when a cell contains a number greater than n.

    >>> foo = SudokuMatrix(n=9)
    >>> foo.add_filled_cell(0,0,10)
    Traceback (most recent call last):
        ...
    CellViolation: ERROR: cell at (0, 0) has value of 10; must have value <= 9.
    >>> foo.choices
    []
    >>> foo.set_grid([10] + [0]*79 + [10])
    ERROR: cell at (0, 0) has value of 10; must have value <= 9.
    ERROR: cell at (8, 8) has value of 10; must have value <= 9.

    """
    def __init__(self, row, col, digit, n):
        self.location = (row, col)
        self.digit = digit
        self.n = n
    def __str__(self):
        return ("ERROR: cell at %s has value of %s; must have value <= %s."
                % (self.location, self.digit, self.n))

class RowViolation(RuleViolation):
    """Raised when a row contains the same digit more than once."""
    pass
class ColumnViolation(RuleViolation):
    """Raised when a column contains the same digit more than once."""
    pass
class BoxViolation(RuleViolation):
    """Raised when a box contains the same digit more than once."""
    pass


if __name__ == "__main__":
    """Run as a standalone script."""
    
    import cgi
    
    # Find a solution to the grid described by the arguments.
    args = cgi.FieldStorage()
    if 'original_grid' in args:
    
        ## Debugging output
        # import cgitb
        # cgitb.enable()
    
        # Header
        print('Content Type: text/json\n')
    
        original_grid = args.getfirst('original_grid')

        # Optional argument n
        n = int(args.getfirst('n', _N))
            
        # Optional argument boxWidth
        boxWidth = int(args.getfirst('boxWidth', _BOX_WIDTH))

        # Fail silently
        try:
            print find_solutions(original_grid, n, boxWidth)
        except Exception:
            print original_grid
        
    # No arguments, so do a doctest.
    else:
        import doctest
        doctest.testmod()
