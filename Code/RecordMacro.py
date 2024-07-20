from sys import exit
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS
import pickle
import time
from pynput.keyboard import Key, Listener, Controller, _NORMAL_MODIFIERS

MACRO_FILENAME:str = r"F:\GitHub\PythonRecordMacro\Code\dist\MacroRecording.txt"
TIMEOUT_DURATION = 15       # Seconds before script times out and closes itself
TimeoutStart = time.time()  # I reset this variable back to time.time() everytime there is a key pressed
                            # This allows for the script to timeout only if left idle

InputRecord:list = []
ModifiedKeyCodes:tuple = ([Key],[])
ModiferPressed:bool = None
Keyboard = Controller()

# https://code.activestate.com/recipes/474070-creating-a-single-instance-application/
class SingletonInstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = "testmutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.mutexname)
        self.lasterror = GetLastError()

    def AlreadyRunning(self):
        return (self.lasterror == ERROR_ALREADY_EXISTS)

    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)

def SaveMacroToFile(inputRecord:list, fileName:str):
    if len(inputRecord) == 0:
        print("InputRecord was empty. Exiting")
        return
    if not fileName:
        print("FileName was empty. Exiting")
        return

    with open(fileName, "wb") as pickleFile:
        pickle.dump(inputRecord, pickleFile)
        print(f"Saved Macro: {inputRecord} to File: '{fileName}'")


def on_press(key):
    global ModiferPressed
    global TimeoutStart
    TimeoutStart = time.time()

    # If there is no Modifier already pressed and the key that was just pressed is of type Key and is a Modifier
    if not ModiferPressed and isinstance(key, Key) and key.value in _NORMAL_MODIFIERS:
        print(f"Modifier pressed: {key}")
        ModiferPressed = key
        ModifiedKeyCodes[0][0] = _NORMAL_MODIFIERS[key.value]   # Set the value of the Modifier Key in the tuple,
                                                                # it needed to be in a List due to tuples being immutable - hence the [0][0]
        return

    if ModiferPressed:
        # Exits out of Macro Record mode if the hotkey RightAlt+RightShift is pressed
        if ModiferPressed == Key.alt_gr and key == Key.shift_r:
            print("Finshed Macro Record")
            SaveMacroToFile(InputRecord, MACRO_FILENAME)
            return False    # Stop listener

        print(f'Modified {key} press')
        ModifiedKeyCodes[1].append(key) # Adds Modified Key/KeyCode to the ModifiedKeyCodes Tuple at the index 1
                                        # which is a list of Modified Keys/KeyCodes pressed while the Modifier Key is being held down.
    else:
        print(f'{key} press')
        InputRecord.append(key)

def on_release(key):
    print(f'{key} release')

    global ModiferPressed

    # On key release if that key is a of type Key and matches the currently pressed
    # Modifier then add the recorded ModifiedKeyCodes to the InputRecord and reset the ModiferPressed var
    if ModiferPressed and isinstance(key, Key) and key == ModiferPressed:
        ModiferPressed = None
        modifier = ModifiedKeyCodes[0][0]
        keyCodes = list(ModifiedKeyCodes[1])
        InputRecord.append((modifier,keyCodes))
        ModifiedKeyCodes[1].clear()


def main():
    myApp = SingletonInstance()
    if myApp.AlreadyRunning():
        print("Another Instance of this program is already running. Exiting")
        exit(0)

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:

        # Will timeout the script after TIMEOUT_DURATION has elapsed with no user input
        while True:
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
    exit(0)

if __name__ == '__main__':
    main()
