"""
Terminal for serial port

Requirement:

    + pyserial
    + py-getch
    + click
"""

import os
from collections import deque
from queue import Queue
import threading
import serial
from io import StringIO
import time
import traceback

import fscloner
from colorprinter import colorize
from serial_utils import setup_serial, send_chunks, clear_bytes
    

def run_terminal(port, baudrate, parity, stopbits, gs_directory, target_directory, verbose):
    device = setup_serial(port, baudrate, parity, stopbits)
    if not device:
        return 0

    print(colorize(f"Syncing ground station at {gs_directory} to {target_directory}.", "teal"))
    
    fscloner.clone_directory(gs_directory, target_directory)
    event_queue = Queue()
    observer = fscloner.synced_observer(target_directory, event_queue, verbose)
    
    print(colorize("Watching for changes. Edit the local clone ONLY WHILE IN REPL!", "teal"))
    print(colorize(f'--- {port} is connected. Press Ctrl+] to quit ---', "teal"))
    
    if os.name == "nt":
        os.system('title CubeSat Ground Station Terminal: Connected')
    
    in_queue = deque()
    def read_input():
        if os.name == 'nt':
            from msvcrt import getch
        else:
            import sys, tty, termios
            stdin_fd = sys.stdin.fileno()
            tty_attr = termios.tcgetattr(stdin_fd)
            tty.setraw(stdin_fd)
            getch = lambda: sys.stdin.read(1).encode()

        while device.is_open:
            ch = getch()
            if ch == b'\x1d':                   # 'ctrl + ]' to quit
                break
            if ch == b'\x00' or ch == b'\xe0':  # arrow keys' escape sequences
                ch2 = getch()
                esc_dict = { b'H': b'A', b'P': b'B', b'M': b'C', b'K': b'D', b'G': b'H', b'O': b'F' }
                if ch2 in esc_dict:
                    in_queue.append(b'\x1b[' + esc_dict[ch2])
                else:
                    in_queue.append(ch + ch2)
            else:  
                in_queue.append(ch)

        if os.name != 'nt':
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, tty_attr)
    
    def strip_clone_dir(path):
        if path.startswith(target_directory):
            return path[len(target_directory):].lstrip("\\/")
        return path
    
    preamble = "from repl import TerminalLink"
    
    def generate_command(event):
        if event[0] == "modify":
            file_path = event[1]
            print(colorize(f"Syncing modified file: {file_path}", "teal"))
            with open(file_path, "r") as f:
                contents = repr(f.read())  # Escape file contents using repr()
            file_path_device = strip_clone_dir(file_path)
            return f"\r\n{preamble}; TerminalLink.modify(r'{file_path_device}', {contents})"
        elif event[0] == "create_file":
            file_path = event[1]
            print(colorize(f"Syncing created file: {file_path}", "teal"))
            # Non-empty files can be created without a "modify" event - cannot assume empty
            with open(file_path, "r") as f:
                contents = repr(f.read())
            file_path_device = strip_clone_dir(file_path)
            return f"\r\n{preamble}; TerminalLink.create_file(r'{file_path_device}', {contents})"
        elif event[0] == "create_dir":
            dir_path = event[1]
            print(colorize(f"Syncing created directory: {dir_path}", "teal"))
            dir_path_device = strip_clone_dir(dir_path)
            return f"\r\n{preamble}; TerminalLink.create_dir(r'{dir_path_device}')"
        elif event[0] == "delete":
            path = event[1]
            print(colorize(f"Syncing deletion: {path}", "teal"))
            path_device = strip_clone_dir(path)
            return f"\r\n{preamble}; TerminalLink.delete(r'{path_device}')"
        elif event[0] == "move":
            source_path, target_path = event[1], event[2]
            print(colorize(f"Syncing move: {source_path} -> {target_path}", "teal"))
            source_path_device = strip_clone_dir(source_path)
            target_path_device = strip_clone_dir(target_path)
            return f"\r\n{preamble}; TerminalLink.move(r'{source_path_device}', r'{target_path_device}')"
        else:
            raise Exception("Unknown event type")
    
    
    thread = threading.Thread(target=read_input)
    thread.start()
    
    # File reception
    receiving_file = False
    delimiter = "***FILE***"
    directory = "terminalfiles"
    buf = StringIO()
    out_queue = deque([None] * len(delimiter))
    
    # REPL communication
    chunk_size = 1024
    
    while thread.is_alive():
        try:
            # Write user input to device
            length = len(in_queue)
            if length > 0:
                device.write(b''.join(in_queue.popleft() for _ in range(length)))

            # Read device output
            line = device.readline()
            if line:
                line_data = line.decode(errors='replace')
                for char in line_data:
                    out_queue.popleft()
                    out_queue.append(char)
                    if not receiving_file:
                        print(char, end="", flush=True)
                        if all(delimiter[i] == v for i,v in enumerate(out_queue)):
                            receiving_file = True
                    else:
                        buf.write(char)
                        if all(delimiter[i] == v for i,v in enumerate(out_queue)):
                            receiving_file = False
                            formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                            if not os.path.exists(directory):
                                os.mkdir(directory)
                            filename = os.path.join(directory, f"{formatted_time}.jpeg")
                            with open(filename, "w") as f:
                                f.write(buf.getvalue()[:-len(delimiter)])
                            print(colorize(f" (saved to {os.getcwd()}\\{filename})", "teal"), flush=True)
                            buf.truncate(0)
            
            # Process changes made to the local clone
            while not event_queue.empty():
                event = event_queue.get()
                command = generate_command(event)
                
                # Send command to REPL, using chunks for large files
                if len(command) > chunk_size:
                    success = send_chunks(device, command, chunk_size, verbose)
                    if not success:
                        print(colorize("Attempt timed out: file likely too large.", "orange"))
                else:
                    device.write(bytes(command, "utf-8"))
                    clear_bytes(device, len(command))
                
                # Enter the command in REPL
                device.write(bytes("\r\n", "utf-8"))

                # to do: add REPL detection, update CPy to 9.0.0+, update mpy's, remove preamble
                # on first connection, check out_queue for ">>> "
                # then match " | something | " with regex
                # tasklist /fi "imagename eq cmd.exe" /fo list /v
        
        except IOError as e:
            print(colorize('--- {} is disconnected ---'.format(port), "orange"))
            break
        
        except Exception as e:
            print(colorize(f"Unknown error: {traceback.format_exc(e)}", "orange"))

    device.close()
    observer.stop()
    observer.join()
    if os.name == "nt":
        os.system('title CubeSat Ground Station Terminal: Disconnected')
    if thread.is_alive():
        print(colorize('--- Press R to reconnect the device, or press Enter to exit ---', "teal"))
        thread.join()
        if in_queue and in_queue[0] in (b'r', b'R'):
            return 1
    return 0
