:: Check for Python Installation
python --version
if errorlevel 1 goto errorNoPython

:: Reaching here means Python is installed.
pip install -r requirements.txt

:: Once done, exit the batch file -- skips executing the errorNoPython section
goto:eof

:errorNoPython
echo.
echo Error^: Python not installed or not added to the Path system variable
pause