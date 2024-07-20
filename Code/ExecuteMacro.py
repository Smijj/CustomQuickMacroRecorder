import pickle
from pynput.keyboard import Controller, _NORMAL_MODIFIERS

MACRO_FILENAME:str = r"F:\GitHub\PythonRecordMacro\Code\dist\MacroRecording.txt"

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

def LoadMacrofromFile(fileName:str) -> list:
    inputRecord:list = []
    try:
        print(f"Attemping to load file: '{fileName}'")
        pickleFile = open(fileName, "rb")
    except FileNotFoundError:
        print(f"Couldn't find file: '{fileName}'. Exiting")
        exit()
    else:
        with pickleFile:
            inputRecord = pickle.load(pickleFile)
            print(f"Loaded Macro: {inputRecord}")

    if len(inputRecord) == 0:
        print("Macro was Empty. Exiting")
        exit()

    return inputRecord


InputRecord = LoadMacrofromFile(MACRO_FILENAME)
ExecuteMacro(InputRecord)
