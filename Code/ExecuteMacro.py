import os, sys, time
import pickle
from pynput.keyboard import Controller, Key, _NORMAL_MODIFIERS

TYPING_DELAY:float = 0.005    # 5ms
MACRO_FILENAME:str = r"\MacroRecording.txt"
MACRO_FILEPATH:str
if getattr(sys, 'frozen', False):
    MACRO_FILEPATH = os.path.dirname(sys.executable) + MACRO_FILENAME
else:
    MACRO_FILEPATH = os.path.dirname(os.path.abspath(__file__)) + MACRO_FILENAME
print(MACRO_FILEPATH)


InputRecord:list = []
Keyboard = Controller()

def ExecuteMacro(inputRecord:list):
    for entry in inputRecord:
        # If the entry is a dict it means its either a set of Modified inputs or a Special Func  
        if isinstance(entry, dict):
            HandleDictEntry(entry)
        else:
            try:
                Keyboard.tap(entry)
                time.sleep(TYPING_DELAY)
                print(f"Pressed: {entry}")
            except:
                print(f"Cannot type entry: {entry}")

def HandleDictEntry(dEntry:dict):
    modifier:Key = dEntry.get("Modifier", False)
    modifiedKeyCodes:list = dEntry.get("KeyCodes", False)
    # modifiedKeyCodes:list = ["AutoNum", 1, 0, 2]  # For Debuging

    if modifier is False or modifiedKeyCodes is False:
        print("Invalid Key's to access Modifier or Keycodes in ModifiedInput Dictionary.")
        return

    if len(modifiedKeyCodes) == 0:
        print("No Modified keys to press.")
        return

    if modifiedKeyCodes[0] == "AutoNum":
        AutoIncrement(modifiedKeyCodes)
    else:
        with Keyboard.pressed(modifier):
            print(f"MODIFIER: {modifier}")
            for keyCode in modifiedKeyCodes:
                Keyboard.tap(keyCode)
                time.sleep(TYPING_DELAY)
                print(f"Pressed Modified: {keyCode}")

def AutoIncrement(keyCodes:list):
    incrementStr:str = ""

    # Type the increment number (default 0) - should be a bunch of seperate ints after the "AutoNum" entry
    if len(keyCodes) == 1:
        # Just incase the "AutoNum" element was the only thing in the ModifiedKeyCodes list then just type 0
        Keyboard.tap("0")
        time.sleep(TYPING_DELAY)
    else:
        # Go through and type out all the numbers after the "AutoNum" entry
        for i in range(1,len(keyCodes)):
            keyStr:str = str(keyCodes[i])
            incrementStr += keyStr
            Keyboard.tap(keyStr)
            time.sleep(TYPING_DELAY)

    # Join them all into a single int and increment the number by 1,
    newIncrement:int = int(incrementStr) + 1
    incrementStr = str(newIncrement)

    # Split the new number back up into seperate numbers and save it back to the macro file
    keyCodes.clear()
    keyCodes.append("AutoNum")
    keyCodes.extend(int(i) for i in incrementStr)
    SaveMacroToFile(InputRecord, MACRO_FILEPATH)


## Saves InputRecord list to a binary file, preserving all the Types
def SaveMacroToFile(inputRecord:list, filePath:str):
    if len(inputRecord) == 0:
        print("InputRecord was empty. Exiting")
        return
    if not filePath:
        print("FileName was empty. Exiting")
        return

    with open(filePath, "wb") as pickleFile:
        pickle.dump(inputRecord, pickleFile)
        print(f"Saved Macro: {inputRecord} to File: '{filePath}'")

## Loads binary file containing Macro info from a filepath and returns a list with the Macro inputs
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

    return inputRecord


def main():
    global InputRecord
    InputRecord = LoadMacrofromFile(MACRO_FILEPATH)
    if len(InputRecord) == 0:
        print("Macro was Empty. Exiting")
        exit(0)

    ExecuteMacro(InputRecord)

if __name__ == '__main__':
    main()
