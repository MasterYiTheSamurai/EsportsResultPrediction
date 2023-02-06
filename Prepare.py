import os
import shutil


def function():
    print("Removing contents of future folder.")
    folder = os.getcwd() + "/future/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename in os.listdir(folder):
        try:
            os.remove(folder + filename)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (filename, e))
    if not os.path.exists(folder):
        os.makedirs(folder)
    print("Preparation phase is done.")


function()
