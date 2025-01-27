Core code based on [Terminal S by makerdiary](https://github.com/makerdiary/terminal-s)

This folder contains the CubeSat ground station terminal. After you have connected the FeatherS2 to your computer via USB, navigate to this folder in Command Prompt or shell and run `python main.py` to open the terminal. You may need to install the `pyserial` module.

The terminal will create a local copy of the ground station's file system in the clonedir folder. While the terminal is connected and the ground station's CircuitPython is in REPL, all changes made to the local copy will be applied to the ground station.

Receiving files in real time from the ground station is possible. The ground station will need to print the following sequence:

```
***FILE***[contents]***FILE***
```

and the terminal will save the contents to the terminalfiles folder, with the file name being the time that the file was received.
