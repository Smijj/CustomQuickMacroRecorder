import pickle
from pynput.keyboard import Key, Listener, Controller, _NORMAL_MODIFIERS

MACRO_FILENAME:str = r"F:\GitHub\PythonRecordMacro\Code\dist\MacroRecording.txt"

InputRecord:list = []
ModifiedKeyCodes:tuple = ([Key],[])
ModiferPressed:bool = None
keyboard = Controller()

""" def ExecuteMacro(inputRecord):
    for entry in inputRecord:
        if isinstance(entry, tuple):
            # print(f"{inp} is a Tuple of Modified Inputs")
            with keyboard.pressed(entry[0]):
                print(f"MODIFIER: {entry[0]}")
                for keyCode in entry[1]:
                    keyboard.tap(keyCode)
                    print(f"Pressed Modified: {keyCode}")
        else:
            keyboard.tap(entry)
            print(f"Pressed: {entry}") """

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
    while True:
        # Collect events until released
        with Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()

        if not listener.running:
            print("Exit")
            break

if __name__ == '__main__':
    main()
