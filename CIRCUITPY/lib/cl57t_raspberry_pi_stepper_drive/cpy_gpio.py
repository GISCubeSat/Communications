import board
import digitalio

BCM = "BCM"
BOARD = "BOARD"
IN = digitalio.Direction.INPUT
OUT = digitalio.Direction.OUTPUT
HIGH = True
LOW = False
PUD_UP = digitalio.Pull.UP
PUD_DOWN = digitalio.Pull.DOWN

_pins = {}

def setmode(mode):
    # CircuitPython doesn't use modes like BCM/BOARD, so this is a no-op
    pass

def setwarnings(flag):
    # No warnings handling needed in CircuitPython, so this is a no-op
    pass

def setup(pin, direction, initial=None, pull_up_down=None):
    if pin not in _pins:
        _pins[pin] = digitalio.DigitalInOut(getattr(board, f"D{pin}"))
    _pins[pin].direction = direction
    if pull_up_down is not None:
        _pins[pin].pull = pull_up_down
    if initial is not None and direction == OUT:
        _pins[pin].value = initial

def output(pin, value):
    if pin in _pins and _pins[pin].direction == OUT:
        _pins[pin].value = value

def input(pin):
    if pin in _pins and _pins[pin].direction == IN:
        return _pins[pin].value
    return None

def cleanup(pin=None):
    global _pins
    if pin is None:
        for p in _pins.values():
            p.deinit()
        _pins.clear()
    elif pin in _pins:
        _pins[pin].deinit()
        del _pins[pin]

def remove_event_detect(pin):
    # CircuitPython doesn't support interrupts in the same way, so this is a no-op
    pass
