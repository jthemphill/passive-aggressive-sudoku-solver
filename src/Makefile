#Makefile for Passive-Aggressive Sudoku Solver
#
# To build your software just type:
#
#     make
#

# ----- Make rules -----

all:	concatenation.js	compiled.js

clean:
	rm concatenation.js compiled.js 

concatenation.js: src/cell.coffee	src/grid.coffee	src/settings.coffee	src/utility.coffee
	coffee -w -c -b -j src/cell.coffee src/grid.coffee src/settings.coffee src/utility.coffee

# Uses the Google JavaScript compiler.
compiled.js:	concatenation.js
	java -jar ../lib/compiler.jar --js ./concatenation.js --js_output_file ./compiled.js	


# N.B.  In the rules above, indented lines are indented with a single
# a tab char (ASCII character 8), and not using spaces.  Do not use
# spaces to indent rule actions.
