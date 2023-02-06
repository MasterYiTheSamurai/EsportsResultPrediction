import os
import shutil


def function():
    print("Removing contents of future folder.")
    folder = os.getcwd() + "/future/"
    for filename in os.listdir(folder):
        try:
            os.remove(folder + filename)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (filename, e))
    print("Preparation phase is done.")


function()
