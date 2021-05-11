#!/usr/bin/python

import os, sys, signal
import libs.bt3api, libs.bt3out, libs.bt3in, libs.bt3ver
import modules.menu

def main():
    signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)
    libs.bt3out.print_banner(libs.bt3ver.__version__, libs.bt3ver.__author__)
    try:
        bt3_cli = modules.menu.Menu()
        bt3_cli.prompt = libs.bt3out.print_prompt(None)
        bt3_cli.cmdloop()

    except Exception as e:
        libs.bt3out.print_error("%s.\n" % e)


if __name__ == '__main__':

    if os.geteuid() != 0:
        print("")
        libs.bt3out.print_error("Blue Team Training Cockpit Toolkit must be started with root (or sudo) privileges.\n")
        sys.exit(1)

    if sys.version_info <= (2,7,9):
        print("")
        libs.bt3out.print_error("Blue Team Training Cockpit Toolkit requires Python 3.8.0")
        libs.bt3out.print_error("Python 3.8.0 is the minimum supported version.\n")
        libs.bt3out.print_error("Check the official documentation for minimum system requirements.\n")
        sys.exit(1)

    if len(sys.argv) == 2 and sys.argv[1].replace("\n", "").upper() in ["INSTALL"]:
        libs.bt3api.stats_counter()
        sys.exit(0)

    else:
        main()
        sys.exit(0)
