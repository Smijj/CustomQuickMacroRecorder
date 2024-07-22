import os, sys
import pickle
from pynput.keyboard import Controller, _NORMAL_MODIFIERS

MACRO_FILENAME:str = r"\MacroRecording.txt"
MACRO_FILEPATH:str
if getattr(sys, 'frozen', False):
    MACRO_FILEPATH = os.path.dirname(sys.executable) + MACRO_FILENAME
else:
    MACRO_FILEPATH = os.path.dirname(os.path.abspath(__file__)) + MACRO_FILENAME
print(MACRO_FILEPATH)

InputRecord:list = []
keyboard = Controller()

def ExecuteMacro(inputRecord:list):
    for entry in inputRecord:
        if isinstance(entry, tuple):
            with keyboard.pressed(entry[0]):
                print(f"MODIFIER: {entry[0]}")
                for keyCode in entry[1]:
                    keyboard.tap(keyCode)
                    print(f"Pressed Modified: {keyCode}")
        else:
            keyboard.tap(entry)
            print(f"Pressed: {entry}")

def LoadMacrofromFile(filePath:str) -> list:
    inputRecord:list = []
    try:
        print(f"Attemping to load file: '{filePath}'")
        pickleFile = open(filePath, "rb")
    except FileNotFoundError:
        print(f"Couldn't find file: '{filePath}'. Exiting")
        exit()
    else:
        with pickleFile:
            inputRecord = pickle.load(pickleFile)
            print(f"Loaded Macro: {inputRecord}")

    if len(inputRecord) == 0:
        print("Macro was Empty. Exiting")
        exit()

    return inputRecord


InputRecord = LoadMacrofromFile(MACRO_FILEPATH)
ExecuteMacro(InputRecord)
