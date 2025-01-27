import platform
import os
import string
import ctypes
from colorprinter import colorize


def detect_external_drives():
    system = platform.system()
    
    if system == "Windows":
        # Windows logic
        drives = []
        # Get bitmask of logical drives
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if bitmask & 1:  # Check if the drive is present
                drive_path = f"{letter}:\\"
                # Filter only removable drives (e.g., USB drives)
                if ctypes.windll.kernel32.GetDriveTypeW(drive_path) == 2:  # DRIVE_REMOVABLE
                    drives.append(drive_path)
            bitmask >>= 1
        return drives
    
    elif system == "Darwin":  # macOS
        # macOS logic
        volumes_path = "/Volumes"
        if os.path.exists(volumes_path):
            return [os.path.join(volumes_path, d) for d in os.listdir(volumes_path)]
        return []
    
    elif system == "Linux":
        # Linux logic
        media_paths = ["/media", "/run/media"]
        drives = []
        for base_path in media_paths:
            if os.path.exists(base_path):
                for root, dirs, _ in os.walk(base_path):
                    for d in dirs:
                        drives.append(os.path.join(root, d))
        return drives
    
    return []


def select_drive():
    external_drives = detect_external_drives()
    if not external_drives:
        print(colorize("--- No external drives detected ---", "orange"))
        return None
    elif len(external_drives) == 1:
        gs_directory = external_drives[0]
        print(colorize(f"--- Auto-detected drive: {gs_directory} ---", "teal"))
        return gs_directory
    else:
        print(colorize("--- Available External Drives ---", "teal"))
        for i, drive in enumerate(external_drives):
            print(colorize(f"  {i}: {drive}", "teal"))
        try:
            selection = int(input(colorize("Select a drive by index: ", "teal")))
            gs_directory = external_drives[selection]
            return gs_directory
        except (ValueError, IndexError):
            print(colorize("--- Invalid selection ---", "orange"))
            return None


# Example Usage
if __name__ == "__main__":
    external_drives = detect_external_drives()
    if external_drives:
        print("Detected external drives:")
        for drive in external_drives:
            print(f" - {drive}")
    else:
        print("No external drives detected.")
