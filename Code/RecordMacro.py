from pynput.keyboard import Key, Listener, Controller, _NORMAL_MODIFIERS

InputRecord = []
ModifiedKeyCodes = ([Key],[])
ModiferPressed = False
keyboard = Controller()

def OutputInputRecord(inputRecord):
    for inp in inputRecord:
        if isinstance(inp, tuple):
            print(f"{inp} is a Tuple of Modified Inputs")
            with keyboard.pressed(inp[0]):
                for keyCode in inp[1]:
                    keyboard.tap(keyCode)
        else:
            keyboard.tap(inp)
            print(f"Pressed: {inp}")

        

def on_press(key):
    if isinstance(key, Key) and key.value in _NORMAL_MODIFIERS:
        print(f"Modifier pressed: {key}")
        global ModiferPressed
        ModiferPressed = True
        ModifiedKeyCodes[0][0] = _NORMAL_MODIFIERS[key.value]
        return
    
    if ModiferPressed:
        print(f'Modified {key} press')
        ModifiedKeyCodes[1].append(key)
    else:
        print(f'{key} press')
        if key != Key.esc:
            InputRecord.append(key)


def on_release(key):
    print(f'{key} release')

    global ModiferPressed
    if ModiferPressed and isinstance(key, Key):
        ModiferPressed = False
        modifier = ModifiedKeyCodes[0][0]
        keyCodes = list(ModifiedKeyCodes[1])
        InputRecord.append((modifier,keyCodes))
        ModifiedKeyCodes[1].clear()

    if key == Key.esc:
        print(InputRecord)
        OutputInputRecord(InputRecord)
        # Stop listener
        return False

while True:
    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    if not listener.running:
        print("Exit")
        break
