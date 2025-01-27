import click
from terminal import run_terminal
from detectdrives import select_drive
from serial.tools import list_ports
from colorprinter import colorize
import os


if os.name == 'nt':
    os.system('title CubeSat Ground Station Terminal')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--port', default=None, help='Serial port name')
@click.option('-b', '--baudrate', default=115200, help='Set baudrate')
@click.option('--parity', default='N', type=click.Choice(['N', 'E', 'O', 'S', 'M']), help='Set parity')
@click.option('-s', '--stopbits', default=1, help='Set stop bits')
@click.option('-l', is_flag=True, help='List serial ports')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def main(port, baudrate, parity, stopbits, l, verbose):
    if port is None:
        ports = list_ports.comports()
        if not ports:
            print(colorize('--- No serial port available ---', "teal"))
            return
        if len(ports) == 1:
            port = ports[0][0]
            print(colorize(f'--- Auto-detected port: {port} ---', "teal"))
        else:
            print(colorize('--- Available Ports ---', "teal"))
            for i, v in enumerate(ports):
                print(colorize(f'--- {i}: {v[0]} {v[2]}', "teal"))
            if l:
                return
            raw = input(colorize('--- Select port index: ', "teal"))
            try:
                n = int(raw)
                port = ports[n][0]
            except ValueError:
                print("--- Invalid selection ---")
                return

    cwd = os.path.basename(os.getcwd())
    if cwd != "ground_station_env":
        response = input(colorize(f"Unrecognized working directory: {os.getcwd()}. Is this correct? (y/n) ", "orange"))
        if response.strip().lower() != "y":
            return

    gs_directory = select_drive()
    if gs_directory is None:
        return

    target_directory = "clonedir"
    while run_terminal(port, baudrate, parity, stopbits, gs_directory, target_directory, verbose):
        pass


if __name__ == "__main__":
    main()
