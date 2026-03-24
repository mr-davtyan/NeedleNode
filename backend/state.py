# backend/state.py

class ScanState:
    def __init__(self):
        self.is_scanning = False
        self.processed = 0
        self.total = 0
        self.current_file = ""
        self.stop_requested = False

    def reset(self):
        self.is_scanning = False
        self.processed = 0
        self.total = 0
        self.current_file = ""
        self.stop_requested = False

class ImportState:
    def __init__(self):
        self.is_importing = False
        self.processed = 0
        self.total = 0
        self.current_file = ""
        self.stop_requested = False

    def reset(self):
        self.is_importing = False
        self.processed = 0
        self.total = 0
        self.current_file = ""
        self.stop_requested = False

# Singleton instances
scan_state = ScanState()
import_state = ImportState()
