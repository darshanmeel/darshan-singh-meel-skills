"""Thin terminal shell over logic.py: redraws the full state after every key.
Run: python prototypes/<name>/tui.py
Piped input is read one character per key: echo aasq | python prototypes/<name>/tui.py"""
import json
import os
import sys

import logic

# key: (label, action passed to logic.step)
KEYS = {"a": ("add item", "add"), "s": ("submit", "submit"), "c": ("cancel", "cancel")}
TTY = sys.stdin.isatty() and sys.stdout.isatty()


def read_key():
    if not TTY:
        return sys.stdin.read(1) or "q"
    try:
        import msvcrt
        return msvcrt.getwch()
    except ImportError:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def frame(state, last):
    bold, dim, off = ("\033[1m", "\033[2m", "\033[0m") if TTY else ("", "", "")
    print("\033[2J\033[H" if TTY else "-" * 40, end="" if TTY else "\n")
    print(f"{bold}state{off} {dim}after: {last}{off}")
    print(json.dumps(state, indent=2, default=str))
    print("  ".join(f"{bold}[{k}]{off} {label}" for k, (label, _) in KEYS.items()) + f"  {bold}[q]{off} quit")


def main():
    os.system("")  # switches on ANSI escape handling in older Windows consoles
    state, last = logic.initial(), "start"
    while True:
        frame(state, last)
        key = read_key()
        if key == "q":
            break
        if key in KEYS:
            last = KEYS[key][0]
            state = logic.step(state, KEYS[key][1])


main()
