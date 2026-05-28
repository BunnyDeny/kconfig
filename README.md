# Kconfig Build System

A standalone Kconfig build system that generates `.config` and C header files from Kconfig definitions. Built on top of [kconfiglib](https://github.com/ulfalizer/Kconfiglib).

## Requirements

- Python 3.8+
- kconfiglib (includes the `menuconfig` TUI)

### Install kconfiglib

```bash
# Debian / Ubuntu
sudo apt install python3-kconfiglib

# Or via pip
pip3 install kconfiglib
```

Verify installation:

```bash
python3 -c "from kconfiglib import Kconfig; from menuconfig import menuconfig; print('OK')"
```

## Quick Start

```bash
git clone https://github.com/BunnyDeny/kconfig.git
cd kconfig

# Launch interactive TUI to configure
make menuconfig

# Or load a defconfig directly
make defconfig
```

After either command, you get:
- `.config` — full configuration in key=value format
- `include/kconfig.h` — C header with `#define` macros (by default without `CONFIG_` prefix, so `CONFIG_FOO=y` becomes `#define FOO 1`)

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make menuconfig` | Interactive TUI configuration |
| `make defconfig` | Load the default defconfig (`$(DEFAULT_DEFCONFIG)` → `.config` → header) |
| `make xxx_defconfig` | Load `$(DEFCONFIG_DIR)/xxx_defconfig` |
| `make oldconfig` | Merge existing `.config` with defaults for newly added Kconfig symbols |
| `make savedefconfig` | Save current `.config` as a minimal defconfig to `$(DEFCONFIG_DIR)/defconfig` |
| `make mrproper` | Remove `.config`, `.config.old`, and the generated header |

## Configuration Variables

Override these in your own Makefile or via command line to adapt the system to your project layout:

```makefile
# Path to the root Kconfig file that sources all sub-Kconfigs
KCONFIG_ROOT    ?= Kconfig

# Path to the generated .config file
CONFIG_FILE     ?= .config

# Path to the generated C header
CONFIG_HEADER   ?= include/kconfig.h

# Directory containing defconfig files
DEFCONFIG_DIR   ?= configs

# Default defconfig used by `make defconfig` (relative path)
DEFAULT_DEFCONFIG ?= $(DEFCONFIG_DIR)/example_defconfig

# Set to --keep-prefix to preserve CONFIG_ in C macro names
# Default: empty (strips CONFIG_ prefix — CONFIG_FOO=y → #define FOO 1)
HEADER_KEEP_PREFIX ?=
```

### Variable Details

**`KCONFIG_ROOT`** — The top-level Kconfig file. This file typically uses `source` to pull in subsystem Kconfig files (e.g. `source "src/Kconfig"`). kconfiglib parses this tree to build the symbol database.

**`CONFIG_FILE`** — Where the full configuration is saved. kconfiglib writes every symbol with its current value. This file is both the input and output of the configuration process.

**`CONFIG_HEADER`** — Path to the generated C header. Your C/C++ source code includes this header to access configuration values as preprocessor macros. By default, the `CONFIG_` prefix is stripped: `CONFIG_FOO=y` becomes `#define FOO 1`.

**`DEFCONFIG_DIR`** — Directory that holds defconfig files. A defconfig is a *minimal* config — it only records values that differ from symbol defaults. `make xxx_defconfig` auto-looks up this directory: `make myboard_defconfig` loads `configs/myboard_defconfig`.

**`DEFAULT_DEFCONFIG`** — Which defconfig to load when you run `make defconfig` without specifying a name.

**`HEADER_KEEP_PREFIX`** — Set to `--keep-prefix` if you want `CONFIG_FOO=y` to generate `#define CONFIG_FOO 1` instead of `#define FOO 1`. Useful if your existing codebase already uses the `CONFIG_` naming convention.

## Integrating Into Your Project

Add the `tools/` directory and `Makefile` to your project, then customize:

```makefile
# In your project's Makefile, before including the kconfig Makefile:
KCONFIG_ROOT    := Kconfig
CONFIG_FILE     := build/.config
CONFIG_HEADER   := build/include/kconfig.h
DEFCONFIG_DIR   := boards
DEFAULT_DEFCONFIG := $(DEFCONFIG_DIR)/stm32f4_defconfig

include kconfig/Makefile
```

Or simply copy the contents and adjust paths to fit your project structure.

## Writing Kconfig Files

See the example `Kconfig` in this repository for a complete demonstration. Key syntax:

```kconfig
config MY_OPTION
    bool "Enable my feature"
    default y
    help
      Description shown in menuconfig help panel.

config MY_VALUE
    int "A numeric value"
    range 0 1024
    default 256

choice
    prompt "Select one"
    default OPTION_A

config OPTION_A
    bool "Option A"

config OPTION_B
    bool "Option B"
endchoice
```

Use `source "path/to/other/Kconfig"` to split large configurations across files.

## License

MIT
