import sys
from cx_Freeze import setup, Executable
exe = Executable(
    script = r"main.py",
    base = "Win32GUI",
    )

setup(
    name = "Platformer",
    version = "1.0",
    description = "Pygame game",
    author = "gcx11",
    executables = [exe]
    )
