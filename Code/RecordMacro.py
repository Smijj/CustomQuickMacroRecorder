from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS
import pickle
import sys, os, time, copy
from pynput.keyboard import Key, KeyCode, Listener, Controller, _NORMAL_MODIFIERS


MACRO_FILENAME:str = r"\MacroRecording.txt"
MACRO_FILEPATH:str
if getattr(sys, 'frozen', False):
    MACRO_FILEPATH = os.path.dirname(sys.executable) + MACRO_FILENAME
else:
    MACRO_FILEPATH = os.path.dirname(os.path.abspath(__file__)) + MACRO_FILENAME
print(MACRO_FILEPATH)

TIMEOUT_DURATION = 15       # Seconds before script times out and closes itself
TimeoutStart = time.time()  # I reset this variable back to time.time() everytime there is a key pressed
                            # This allows for the script to timeout only if left idle


InputRecord:list = []
ModifiedInputRecord:dict = {"Modifier":Key, "KeyCodes":[]}
ModifierPressed:bool = False
Keyboard = Controller()

# https://code.activestate.com/recipes/474070-creating-a-single-instance-application/
class SingletonInstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = "testmutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.mutexname)
        self.lasterror = GetLastError()
        print(f"Created Mutex: {self.mutex}")

    def AlreadyRunning(self):
        return self.lasterror == ERROR_ALREADY_EXISTS

    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)


def on_press(key):
    global ModifierPressed
    global TimeoutStart
    TimeoutStart = time.time()

    # If there is no Modifier already pressed and the key that was just pressed is of type Key and is a Modifier
    if not ModifierPressed and isinstance(key, Key) and key.value in _NORMAL_MODIFIERS:
        print(f"Modifier pressed: {key}")
        ModifierPressed = key
        ModifiedInputRecord["Modifier"] = _NORMAL_MODIFIERS[key.value]  # Set the value of the Modifier Key
        return  # Return out of this on_press event as we dont want to record the initial modifer press like a regular key press

    # Handle modified key-press
    if ModifierPressed:
        if HandleModifiedKeyPress(key) is False:
            return False    # Stops listener

    # Handle normal key-press
    else:
        print(f'{key} press')
        InputRecord.append(key)

def on_release(key):
    global ModifierPressed

    # On key release, if that key is a of type Key and matches the currently pressed Modifier
    if ModifierPressed and isinstance(key, Key) and key == ModifierPressed:
        ReleaseModifer()
    # print(f'{key} released')


def HandleModifiedKeyPress(key):
    # The modifier is being held down and will keep triggering so we dont want to listen to the input events from it
    if key == ModifierPressed: return True
    
    modifiedKeyCodes:list = ModifiedInputRecord["KeyCodes"]

    # Right Alt modifier pressed
    if ModifierPressed == Key.alt_gr or ModifierPressed == Key.alt_r:
        
        # Exits out of Macro Record mode if the hotkey RightAlt+RightShift is pressed
        if key == Key.shift_r:
            print("Finshed Macro Record")
            SaveMacroToFile(InputRecord, MACRO_FILEPATH)
            return False    # Stop listener
        
        # Inserts the AutoNum feature if the hotkey RightAlt+N is pressed
        if key == KeyCode.from_char("n"):
            print("Alt+N")
            modifiedKeyCodes.clear() # Clears the modified inputs list to have a fresh list for this function
            modifiedKeyCodes.append("AutoNum")  # Set the first value in the list to a known string
            return True     # Pass the rest of the function
        
        if len(modifiedKeyCodes) > 0 and modifiedKeyCodes[0] is "AutoNum":
            # Ignore any input that is not a KeyCode (excludes modifers and anything that isnt a normal char)
            if not isinstance(key, KeyCode) or key.char is None:
                return True
            
            # Filters out any input that isnt an int
            try:
                keyAsInt:int = int(key.char)
                modifiedKeyCodes.append(keyAsInt)
            except ValueError:
                print(f"{key} is not an int")

            return True

    # Adds Modified Key/KeyCode to the ModifiedInputRecord's 'KeyCodes' - which is a list of Keys/KeyCodes pressed while the Modifier Key is being held down.
    modifiedKeyCodes.append(key)
    
    print(f'Modified {key} press')
    return True

## Add the recorded ModifiedKeyCodes to the InputRecord and reset the ModiferPressed var
def ReleaseModifer():
    global ModifierPressed
    ModifierPressed = False

    modifiedKeyCodes:list = ModifiedInputRecord["KeyCodes"]

    if len(modifiedKeyCodes) > 0:
        # If the AutoNum feature is being used and no manual increment has been entered, start at 0
        if modifiedKeyCodes[0] is "AutoNum" and len(modifiedKeyCodes) == 1:
            modifiedKeyCodes.append(0)
        
        # Append a deepcopy of the dictionary to the InputRecord list if there are any modified keycodes.
        # Needs to Deepcopy as otherwise it wouldnt copy through the nested Lists that are in the Dict
        InputRecord.append(copy.deepcopy(ModifiedInputRecord))
    else:
        # Otherwise just add the modifier that was pressed
        InputRecord.append(ModifiedInputRecord["Modifier"])


    # Reset the the ModifiedInputRecord var
    ModifiedInputRecord["Modifier"] = None
    ModifiedInputRecord["KeyCodes"].clear()

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


def main():
    myApp = SingletonInstance()
    if myApp.AlreadyRunning():
        # print(f"Last Error: {myApp.lasterror}")
        print("Another Instance of this program is already running. Exiting")
        # time.sleep(6)
        sys.exit(0)

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:

        # Will timeout the script after TIMEOUT_DURATION has elapsed with no user input
        while True:
            # print(myApp.lasterror)
            # print(user32.GetMessageW(myApp.myMessageID, 0 ,0 ,0))
            time.sleep(1)
            if time.time() >= TimeoutStart + TIMEOUT_DURATION:
                print("Timeout")
                listener.stop()
                break
            if not listener.running:
                print("Listener Dead")
                break

        listener.join()
    print("Exit")
    sys.exit(0)

if __name__ == '__main__':
    main()
