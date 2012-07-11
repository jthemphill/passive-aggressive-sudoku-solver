PASS (Passive/Agressive Sudoku Solver) is a Sudoku Solver with an
incremental-solve feature.

This project depends on jQuery, Python 2.7, and the Google JavaScript
compiler (although a compiler is not strictly speaking necessary)

All scripting for PASS has been compiled and minified to JavaScript
from the provided CoffeeScript. The contents of this directory are as
follows:

CONTENTS
========

README --> This file.

COPYING --> A copy of the GNU Public License. This software is
licensed under the GPL.
            
grid.coffee --> Contains functions which render the Sudoku Grid on the web
                page.
                
cell.coffee --> Contains setters and handlers for the cells within the grid.

settings.coffee --> Contains setters and handlers for the web app's settings.

utility.coffee --> Contains miscellaneous mathematical and logical functions.

sudoku.py --> A copy of the CGI script used to solve the puzzle.
