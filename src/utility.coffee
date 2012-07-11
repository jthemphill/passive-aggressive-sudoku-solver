# Constants
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITLENGTH = 35

## Utility functions ##

midFactor = (x) ->
    ###
    Return the factor of X closest to its square root.
    ###
    rootX = Math.floor(Math.sqrt(x))
    for i in [rootX..1]
        if x % i == 0
            return i
    return x

intDivide = (numerator, denominator) ->
    ###
    Return (numerator // denominator) using integer floor division.
    ###
    remainder = (numerator % denominator)
    ((numerator - remainder) / denominator)

toInteger = (x) ->
    ###
    Convert the string x to an integer.
    ###
    for i in [0...DIGITLENGTH]
        if (x == DIGITS[i])
            return i

## Page Loading Script ##
loadPage = () ->
    ###
    If the values in the settings form are valid, render the grid with the
    user-input dimensions.
    ###

    if (BOX_WIDTH() * BOX_HEIGHT() == N())
        render()

## startup script follows ##
$(document).ready(->
    # Since JavaScript seems to be working,
    # remove the noscript section from the DOM.
    $('#noscript').detach()

    # Bind handlers to input fields
    $('#groupSizeInput').bind('input', handleGroupSizeInput)
    $('#boxWidthInput').bind('input', handleBoxWidthInput)
    $('#boxHeightInput').bind('input', handleBoxHeightInput)

    loadPage()
)
