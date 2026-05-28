#!/usr/bin/env python3
"""
Load a defconfig (minimal diff) into .config (full config),
then optionally generate a C header.

Usage:
    python3 tools/load_defconfig.py configs/foo_defconfig
    python3 tools/load_defconfig.py configs/foo_defconfig -H include/kconfig.h
    python3 tools/load_defconfig.py configs/foo_defconfig -k path/Kconfig -c path/.config
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from kconfiglib import Kconfig
except ImportError:
    print("Error: kconfiglib is not installed.")
    print("Please run:  sudo apt install python3-kconfiglib")
    print("          or: pip3 install kconfiglib")
    sys.exit(1)

import config_to_header


def main():
    parser = argparse.ArgumentParser(
        description="Load a defconfig into .config and optionally generate a C header")
    parser.add_argument("defconfig", help="Path to the defconfig file")
    parser.add_argument("-k", "--kconfig", default="Kconfig",
                        help="Path to root Kconfig file (default: Kconfig)")
    parser.add_argument("-c", "--config", default=".config",
                        help="Path to output .config file (default: .config)")
    parser.add_argument("-H", "--header",
                        help="Path to generated C header")
    args = parser.parse_args()

    if not os.path.exists(args.defconfig):
        print(f"Error: {args.defconfig} not found")
        sys.exit(1)

    if not os.path.exists(args.kconfig):
        print(f"Error: {args.kconfig} not found")
        sys.exit(1)

    kconfig = Kconfig(args.kconfig)
    kconfig.load_config(args.defconfig)
    kconfig.write_config(args.config)
    print(f"Loaded {args.defconfig} into {args.config}")

    if args.header:
        config_to_header.convert(args.config, args.header)


if __name__ == "__main__":
    main()
