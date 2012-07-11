changeGroupSize = () ->
    ###
    When N is changed, guess at the combination desired by the user
    and modify boxWidth and boxHeight to fit.
    ###

    # Most Sudoku puzzles in the wild have boxes wider than they are long.
    # midFactor returns the lesser of the two middle factors of N.
    n = N()
    boxHeight = midFactor(n)

    setBoxWidth(n / boxHeight)
    setBoxHeight(boxHeight)

    loadPage()

## Handlers ##

handleGroupSizeInput = () ->
    changeGroupSize()

handleBoxWidthInput = () ->
    ###
    When boxWidth is changed, guess at the combination desired by the user
    and modify boxHeight to fit.
    ###

    n = N()
    boxWidth = BOX_WIDTH()

    if (n % boxWidth == 0)
        setBoxHeight(n / boxWidth)

    loadPage()

handleBoxHeightInput = () ->
    ###
    When boxHeight is changed, guess at the combination desired by the user
    and modify boxWidth to fit.
    ###

    n = N()
    boxHeight = BOX_HEIGHT()

    if (n % boxHeight == 0)
        setBoxWidth(n / boxHeight)

    loadPage()

## Getters ##

N = () ->
    Number $("#groupSizeInput").val()

BOX_HEIGHT = () ->
    Number $("#boxHeightInput").val()

BOX_WIDTH = () ->
    Number $("#boxWidthInput").val()

## Setters ##

setGroupSize = (n) ->
    $("#groupSizeInput").val(n)

setBoxWidth = (boxWidth) ->
    $("#boxWidthInput").val(boxWidth)

setBoxHeight = (boxHeight) ->
    $("#boxHeightInput").val(boxHeight)
