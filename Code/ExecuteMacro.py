from pynput.keyboard import Key, Listener, Controller, _NORMAL_MODIFIERS

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