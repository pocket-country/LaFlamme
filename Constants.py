from enum import Enum

# --- 1. TEST STATUS ENUMERATION ---
# The safest way to handle tri-valued results without 0/1 conflicts.
class TestStatus(Enum):
    PASSED = 1        # Success
    FAILED = 2        # Failed core PDA logic
    FILE_ERROR = -1   # Infrastructure failure (missing file, I/O, etc.)

# --- 2. ANSI COLOR CONSTANTS ---
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'  # Pass color
    RED = '\033[91m'    # Fail color
    YELLOW = '\033[93m' # Error color
    BOLD = '\033[1m'

# --- 3. UTF SYMBOL CONSTANTS ---
SYMBOL_PASS = '\u2705'   # ✅
SYMBOL_FAIL = '\u274C'   # ❌
SYMBOL_ERROR = '\u2753'  # ❓
