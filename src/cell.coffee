newCell = (cellNum) ->
    ###
    A Cell is a Text Input Element contained within the Grid.

    Each Cell has a unique id as the string 'cell#{num}' where #{num} is the
    number, from 0 to n**2, of the cell within the Grid.

    This function is essentially a constructor for Cell objects.
    ###

    # x is the cell being created.
    x = document.createElement('input')
    x.type = 'text'
    x.id = "cell#{cellNum}"
    x.className += "cell"

    x.sanitize = () ->
        ###
        Ensure that the value of the cell is valid and standardize its
        representation.
        ###
        @correctErrors()

        newValue = @baseNValue()

        if newValue == 0
            @clearValue()
        @setValue(newValue)

    x.correctErrors = () ->
        ###
        Check for and correct errors in the Cell's value.
        ###
        n = N()
        baseTenValue = @baseTenValue()

        # Correct negative values
        if (baseTenValue < 0)
            @clearValue()

        # Correct values greater than N
        else if (baseTenValue > n)
            @clearValue()

    ## Getters and Setters ##
    x.clearValue = () ->
        ###
        Clear the value of the Cell.
        ###
        @setValue("")

    x.isEmpty = () ->
        ###
        True if the calling Cell is empty.
        ###
        (@value == 0) or (@value == "")

    x.setValue = (newValue) ->
        ###
        Change the Cell's current value to the specified newValue.
        ###
        jQueryThis = $("#{@id}")

        if newValue != @value
            jQueryThis.fadeOut()
            jQueryThis.hide()
            @value = newValue
            jQueryThis.fadeIn()

    ## Conversion functions ##
    x.baseTenValue = () ->
        ###
        Return the value of the cell as a base-10 integer.
        ###
        if @value >= 10
            @value
        else
            DIGITS.search(@value)

    x.baseNValue = () ->
        ###
        Return the value of the cell as a base-N integer.
        ###

        # Convert value to a letter if longer than a single digit
        if (@value >= 10)
            DIGITS[@value]
        else if (@value == "")
            0
        else
            @value

    return x

## Handlers ##
handleCellBlur = () ->
    ###
    Called when Cell loses focus.
    ###
    @sanitize()
    solve()

## Getters and Setters ##
getCell = (cellNum) ->
    ###
    Return the Cell corresponding to cellNum.
    ###
    document.getElementById("cell#{cellNum}")

setCellValue = (cellNum, val) ->
    ###
    Set the value of the Cell corresponding to cellNum.
    ###
    if ((val == 0) or (val == "0"))
        val = ""

    getCell(cellNum).setValue(val)
