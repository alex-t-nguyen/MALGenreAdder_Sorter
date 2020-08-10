@echo off

set /p command="Would you like to add or get genres? [A/G]: "

if "%command%" == "G" goto :getGenre
if "%command%" == "g" goto :getGenre

if "%command%" == "A" goto :addGenre
if "%command%" == "a" goto :addGenre

:getGenre
    set /p command2="Do you want to export a list from MAL or upload a current list? [E/U]: "

    if "%command2%" == "U" goto :uploadFile
    if "%command2%" == "u" goto :uploadFile

    set /p genre="Enter genre of anime to search for: "

    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    python get_genres.py %command2% %genre%

    goto :eof

:addGenre
    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    python add_genres.py

    goto :eof

:uploadFile
    cd C:\Users\AlexN\Documents\Python Projects\MALGenreAdder
    set /p pathname="Enter file path of list to use: "
    set /p genre="Enter genre of anime to search for: "

    python get_genres.py %command% %genre% %pathname%

    goto :eof