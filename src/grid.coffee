###
Passive-Aggressive Sudoku Solver:
Grid Functions.

Jeffrey Hemphill

January 15, 2011
###

render = () ->
    ###
    Render the Sudoku grid with the given dimensions.
    ###

    n = N()
    boxWidth = BOX_WIDTH()
    boxHeight = BOX_HEIGHT()

    # Clear the existing grid.
    $('#sudokuGrid').empty()

    # A running counter of the number of cells we've created.
    cellNum = 0

    ## Columns ##

    # The table contains boxHeight groups of columns.
    for i in [0...boxHeight]
        $('#sudokuGrid').append(document.createElement('colgroup'))

    # Each group contains boxWidth columns.
    for j in [0...boxWidth]
        $('#sudokuGrid colgroup').append(document.createElement('col'))

    ## Rows ##

    # Use cellNum to assign a unique ID to each cell.
    cellNum = 0

    # The table contains boxWidth groups of rows.
    for i in [0...boxWidth]
        tbody = document.createElement('tbody')
        $('#sudokuGrid').append(tbody)

        # Each group contains boxHeight rows.
        for j in [0...boxHeight]
            tr = document.createElement('tr')
            tbody.appendChild(tr)

            # Each row contains n cells.
            for k in [0...n]
                td = document.createElement('td')
                tr.appendChild(td)

                cell = newCell(cellNum++)
                td.appendChild(cell)

    ## Bind Handlers to Cells ##
    $('.cell').blur(handleCellBlur)

gridToString = () ->
    n = N()
    numCells = n * n
    s = ''
    for i in [0...numCells]
        val = getVal(i)
        s += "#{val}"
    s

stringToGrid = (s) ->
    numCells = Math.pow(N(), 2)
    for i in [0...numCells]
        setCellValue(i, s[i])

getVal = (cellNum) ->
    cell = getCell(cellNum)
    cell.baseNValue()

solve = () ->
    ###
    Update the grid with the solution to the puzzle.
    ###
    $.ajax({
        url: "cgi-bin/sudoku.py",
        data: {
            original_grid: gridToString(),
            n: N(),
            boxWidth: BOX_WIDTH()
        },
        ifModified: true,
        success: (data, status, xhr) ->
            stringToGrid(data)
    })

updateGridConstants = () ->
    ###
    Update the global variables describing the size of the grid to the values
    currently in the user form.
    ###

    # Calls to the toInteger function will no longer be necessary once
    # HTML5 is widely supported.
    window.N = toInteger($('#groupSizeInput').attr('value'))
    window.BOXWIDTH = toInteger($('#boxWidthInput').attr('value'))
    window.BOXHEIGHT = toInteger($('#boxHeightInput').attr('value'))

