#!/usr/bin/env python3
"""
Switch Input Method
Usage: py input_method.py "en" / "zh" / "toggle"

Note: This script uses Shift to toggle input method.
Make sure no mouse movement to screen corners during execution.
"""
import sys
import time

def switch_to_english():
    """Switch to English input method (Shift)"""
    import pyautogui
    pyautogui.FAILSAFE = False  # Disable corner fail-safe for this specific action
    pyautogui.press('shift')
    time.sleep(0.1)
    pyautogui.FAILSAFE = True   # Re-enable

def switch_to_chinese():
    """Switch to Chinese input method (Shift)"""
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.press('shift')
    time.sleep(0.1)
    pyautogui.FAILSAFE = True

def toggle():
    """Toggle input method"""
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.press('shift')
    time.sleep(0.1)
    pyautogui.FAILSAFE = True

def main():
    if len(sys.argv) < 2:
        print("Usage: py input_method.py [en|zh|toggle]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    try:
        time.sleep(0.5)  # Ensure focus
        if mode == "en" or mode == "english":
            switch_to_english()
            print("Switched to English input method")
        elif mode == "zh" or mode == "chinese":
            switch_to_chinese()
            print("Switched to Chinese input method")
        elif mode == "toggle":
            toggle()
            print("Toggled input method")
        else:
            print("Invalid mode. Use: en, zh, or toggle", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
