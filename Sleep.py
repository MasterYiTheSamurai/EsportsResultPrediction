import os
import datetime

now = datetime.datetime.now()

def function():
    if now.hour > 23 or now.hour < 10:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    else:
        print("It's not sleeping time.")


function()
