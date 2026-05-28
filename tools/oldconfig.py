#!/usr/bin/env python3
"""
Update an existing .config against the current Kconfig tree,
assigning defaults to any new symbols.

Usage:
    python3 tools/oldconfig.py
    python3 tools/oldconfig.py -k path/Kconfig -c path/.config
    python3 tools/oldconfig.py -H include/kconfig.h   # also regenerate header
"""
import os
import sys
import argparse

try:
    from kconfiglib import Kconfig
except ImportError:
    print("Error: kconfiglib is not installed.")
    print("Please run:  sudo apt install python3-kconfiglib")
    print("          or: pip3 install kconfiglib")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Update .config with defaults for new Kconfig symbols")
    parser.add_argument("-k", "--kconfig", default="Kconfig",
                        help="Path to root Kconfig file (default: Kconfig)")
    parser.add_argument("-c", "--config", default=".config",
                        help="Path to .config file (default: .config)")
    parser.add_argument("-H", "--header",
                        help="Path to generated C header (regenerated if config changed)")
    args = parser.parse_args()

    if not os.path.exists(args.kconfig):
        print(f"Error: {args.kconfig} not found")
        sys.exit(1)

    kconfig = Kconfig(args.kconfig)

    dotconfig = args.config
    if os.path.exists(dotconfig):
        old_mtime = os.path.getmtime(dotconfig)
        kconfig.load_config(dotconfig)
        print(f"Loaded existing config: {dotconfig}")
    else:
        old_mtime = None
        print(f"No existing {dotconfig} found, using defaults.")

    kconfig.write_config(dotconfig)
    print(f"Updated {dotconfig} with defaults for any new symbols")

    if args.header:
        new_mtime = os.path.getmtime(dotconfig)
        if old_mtime is None or new_mtime != old_mtime:
            import config_to_header
            config_to_header.convert(dotconfig, args.header)


if __name__ == "__main__":
    main()
