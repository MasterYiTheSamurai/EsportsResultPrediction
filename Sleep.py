import os


def function():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


function()
