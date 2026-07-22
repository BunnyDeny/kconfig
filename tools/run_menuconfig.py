#!/usr/bin/env python3
"""
Launch the interactive menuconfig TUI.

Usage:
    python3 tools/run_menuconfig.py                  # use ./Kconfig, ./.config
    python3 tools/run_menuconfig.py -k path/Kconfig  # custom Kconfig path
    python3 tools/run_menuconfig.py -k path/Kconfig -c path/.config -H path/output.h

Requires: apt install python3-kconfiglib  (or: pip3 install kconfiglib)
"""
import os
import sys
import argparse

# Add project root to sys.path so local kconfiglib.py is found
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from kconfiglib import Kconfig
    from menuconfig import menuconfig as _menuconfig
except ImportError:
    print("Error: kconfiglib or menuconfig is not installed.")
    print("Please run:  sudo apt install python3-kconfiglib")
    print("          or: pip3 install kconfiglib")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Kconfig TUI (menuconfig)")
    parser.add_argument("-k", "--kconfig", default="Kconfig",
                        help="Path to root Kconfig file (default: Kconfig)")
    parser.add_argument("-c", "--config", default=".config",
                        help="Path to .config file (default: .config)")
    parser.add_argument("-H", "--header",
                        help="Path to generated C header (sync on save)")
    args = parser.parse_args()

    os.environ["MENUCONFIG_STYLE"] = (
        "aquatic "
        "list=fg:white,bg:blue "
        "selection=fg:black,bg:white,bold "
        "inv-list=fg:white,bg:blue "
        "inv-selection=fg:black,bg:white "
        "show-help=fg:white,bg:blue "
        "text=fg:white,bg:blue"
    )

    kconfig = Kconfig(args.kconfig)

    dotconfig = args.config
    if os.path.exists(dotconfig):
        kconfig.load_config(dotconfig)
        print(f"Loaded existing config: {dotconfig}")
        config_mtime_before = os.path.getmtime(dotconfig)
    else:
        print("No existing .config found, using defaults.")
        config_mtime_before = None

    _menuconfig(kconfig)

    if os.path.exists(dotconfig):
        config_mtime_after = os.path.getmtime(dotconfig)
    else:
        config_mtime_after = None

    if config_mtime_after != config_mtime_before:
        if args.header:
            import config_to_header
            config_to_header.convert(dotconfig, args.header)
    else:
        print(f"Configuration changes discarded (not saved to {dotconfig}).")


if __name__ == "__main__":
    main()
