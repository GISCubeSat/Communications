import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


def clone_directory(source_dir, target_dir, verbose=False):
    if os.path.exists(target_dir):        
        # Empty target directory
        for item in os.listdir(target_dir):
            if item == ".git" or item == ".gitignore":
                continue
            to_remove_path = os.path.join(target_dir, item)
            if os.path.isdir(to_remove_path):
                shutil.rmtree(to_remove_path)
            else:
                os.remove(to_remove_path)
        
        # Copy source directory to target directory
        for item in os.listdir(source_dir):
            if item == ".git" or item == ".gitignore":
                continue
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
        
        if verbose: print(f"Updated '{target_dir}' with changes from '{source_dir}'.")
    else:
        # Fresh clone if the target directory doesn't exist
        shutil.copytree(source_dir, target_dir)
        if verbose: print(f"Cloned '{source_dir}' to '{target_dir}'.")


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
    
    def on_created(self, event):
        print(f"File created: {event.src_path}")
    
    def on_deleted(self, event):
        print(f"File deleted: {event.src_path}")
    
    def on_moved(self, event):
        print(f"File moved: {event.src_path} -> {event.dest_path}")


class SyncedChangeHandler(FileSystemEventHandler):
    def __init__(self, event_queue, verbose=False):
        self.event_queue = event_queue
        self.verbose = verbose
    
    def on_modified(self, event):
        if not event.is_directory:  # Disregard modifying directories
            self.event_queue.put(("modify", event.src_path))
            if self.verbose:
                print(f"File modified: {event.src_path}")

    def on_created(self, event):
        if event.is_directory:
            self.event_queue.put(("create_dir", event.src_path))
            if self.verbose:
                print(f"Directory created: {event.src_path}")
        else:
            self.event_queue.put(("create_file", event.src_path))
            if self.verbose:
                print(f"File created: {event.src_path}")

    def on_deleted(self, event):
        self.event_queue.put(("delete", event.src_path))
        if self.verbose:
            print(f"File/directory deleted: {event.src_path}")

    def on_moved(self, event):
        self.event_queue.put(("move", event.src_path, event.dest_path))
        if self.verbose:
            print(f"{'Directory' if event.is_directory else 'File'} moved: {event.src_path} -> {event.dest_path}")


def monitor_directory(directory_to_watch):
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()
    print(f"Monitoring changes in '{directory_to_watch}'. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def synced_observer(directory_to_watch, event_queue, verbose=False):
    event_handler = SyncedChangeHandler(event_queue, verbose)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()
    return observer

# Example usage
if __name__ == "__main__":
    source_directory = "D:"  # Replace with the directory to clone
    target_directory = "clonedir"  # Replace with the local clone directory (e.g., a GitHub repo)

    print(f"Current working directory: {os.getcwd()}")
    
    # Step 1: Clone the directory
    print(f"Attempting to clone '{source_directory}' to '{target_directory}'.")
    clone_directory(source_directory, target_directory, verbose=True)

    # Step 2: Monitor the cloned directory
    monitor_directory(target_directory)
