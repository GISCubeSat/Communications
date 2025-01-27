import serial
from colorprinter import colorize
import time


def setup_serial(port, baudrate, parity, stopbits):
    try:
        device = serial.Serial(port=port,
                               baudrate=baudrate,
                               bytesize=8,
                               parity=parity,
                               stopbits=stopbits,
                               timeout=0.1,
                               write_timeout=4)
        return device
    except serial.SerialException:
        print(colorize(f"--- Failed to open {port} ---", "orange"))
        return None


def send_chunks(device, command, chunk_size=1024, verbose=False):
    '''Send long commands while clearing the REPL echo at the same time.'''
    encoded_command = command.encode("utf-8")
    for i in range(0, len(encoded_command), chunk_size):
        chunk = encoded_command[i:i + chunk_size]
        device.write(chunk)
        device.flush()
        if verbose: print(f"Bytes {i} to {i+chunk_size} sent")
        
        # Wait at most 5 seconds
        count = 0
        while count < 500 and device.in_waiting < len(chunk):
            count += 1
            time.sleep(0.01)
        if count == 500: return False
        
        echo = device.read(device.in_waiting)
        if verbose: print(f"{len(echo)} bytes received")
    return True


def clear_bytes(device, expected_bytes):
    '''Get rid of the echoed command by reading it.'''
    while device.in_waiting < expected_bytes:
        time.sleep(0.01)
    device.read(device.in_waiting)
