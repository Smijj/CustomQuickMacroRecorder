# CustomQuickMacroRecorder

A couple custom scripts to seperately Record and Execute macros.
- The RecordMacro script will listen to, record, and save any keyboard input to a binary file - Terminates with RightAlt+RightShift or after 15 seconds with no input. Only 1 of this program is allowed to run at a time, any additional instances of it will close automatically.
- The ExecuteMacro script will read the file created by the RecordMacro script and execute the keyboard inputs in the exact same order.

I have these built into .exe's that can be launched from an external Keypad. Basic build instructions are in the 'Code/cmd build commands.txt' file.
