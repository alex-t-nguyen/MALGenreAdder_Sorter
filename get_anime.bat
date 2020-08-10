@echo off

:start
    set /p command="Would you like to add or get genres? [A/G]: "

    if /I "%command%" == "G" goto :getGenre

    if /I "%command%" == "A" goto :addGenre

    goto :start

:getGenre
    set /p command2="Do you want to export a list from MAL or upload a current list? [E/U]: "

    if /I "%command2%" == "U" goto :uploadFile

    if /I not "%command2%" == "E" goto :getGenre

    set /p genre="Enter genre of anime to search for: "

    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    python get_genres.py "%command2%" "%genre%"

    goto :eof

:addGenre
    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    python add_genres.py

    goto :eof

:uploadFile
    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    set /p pathname="Enter file path of list to use: "
    set /p genre="Enter genre of anime to search for: "

    python get_genres.py "%command%" "%genre%" "%pathname%"

    goto :eof