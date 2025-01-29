"""
File system utilities that the ground station terminal
can invoke from REPL to sync changes made to the local clone.
"""

import os


class TerminalLink:
    @staticmethod
    def split_path(path):
        """Splits a path into directory and file components."""
        path = path.rstrip("/")  # Remove trailing slash
        if "/" in path:
            directory, file_name = path.rsplit("/", 1)
            return directory, file_name
        return "", path

    @staticmethod
    def modify(file_path, contents):
        with open(file_path, "w") as f:
            f.write(contents)
        print(f"Sync successful: modified {file_path}")
    
    @staticmethod
    def create_file(file_path, contents=""):
        directory, _ = TerminalLink.split_path(file_path)
        if directory and not TerminalLink.exists(directory):
            TerminalLink.create_dir(directory)
        with open(file_path, "w") as f:
            f.write(contents)
        print(f"Sync successful: created file {file_path}")
    
    @staticmethod
    def create_dir(dir_path):
        if not TerminalLink.exists(dir_path):
            # Recursively create parent directories
            parent_dir, _ = TerminalLink.split_path(dir_path)
            if parent_dir and not TerminalLink.exists(parent_dir):
                TerminalLink.create_dir(parent_dir)
            os.mkdir(dir_path)
        print(f"Sync successful: created directory {dir_path}")
    
    @staticmethod
    def delete(path):
        if TerminalLink.is_dir(path):
            # Recursively delete directory contents
            for entry in os.listdir(path):
                full_path = f"{path}/{entry}"
                TerminalLink.delete(full_path)
            os.rmdir(path)
        else:
            os.remove(path)
        print(f"Sync successful: deleted {path}")
    
    @staticmethod
    def move(source_path, target_path):
        target_dir, _ = TerminalLink.split_path(target_path)
        if target_dir and not TerminalLink.exists(target_dir):
            TerminalLink.create_dir(target_dir)
        os.rename(source_path, target_path)
        print(f"Sync successful: moved {source_path} to {target_path}")
    
    @staticmethod
    def exists(path):
        """Checks if a file or directory exists."""
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    @staticmethod
    def is_dir(path):
        """Checks if a path is a directory."""
        try:
            return os.stat(path)[0] & 0o170000 == 0o040000
        except OSError:
            return False
