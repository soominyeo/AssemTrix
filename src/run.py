import sys
from ui import cli, gui

if __name__=="__main__":
    try:
        if "-c" in sys.argv:
            sys.argv.remove("-c")
            cli.run_cli(sys.argv)
        else:
            gui.run_gui(sys.argv)
    finally:
        pass

