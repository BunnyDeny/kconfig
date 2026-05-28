# Kconfig Build System — Template Makefile
#
# Customize these variables for your project:
#   KCONFIG_ROOT     - Path to the root Kconfig file
#   CONFIG_FILE      - Path to the .config file
#   CONFIG_HEADER    - Path to the generated C header
#   DEFCONFIG_DIR    - Directory containing defconfig files
#   DEFAULT_DEFCONFIG - Fallback defconfig when no target is specified
#   HEADER_KEEP_PREFIX - Set to --keep-prefix to preserve CONFIG_ in macros

KCONFIG_ROOT    ?= Kconfig
CONFIG_FILE     ?= .config
CONFIG_HEADER   ?= include/kconfig.h
DEFCONFIG_DIR   ?= configs
DEFAULT_DEFCONFIG ?= $(DEFCONFIG_DIR)/example_defconfig
HEADER_KEEP_PREFIX ?=

TOOLS_DIR       ?= tools

.PHONY: all help menuconfig oldconfig defconfig savedefconfig mrproper

all: help

help:
	@echo "Kconfig Build System"
	@echo ""
	@echo "  make menuconfig        Interactive configuration (TUI)"
	@echo "  make oldconfig         Update .config with defaults for new symbols"
	@echo "  make defconfig         Load default defconfig ($(DEFAULT_DEFCONFIG))"
	@echo "  make xxx_defconfig     Load $(DEFCONFIG_DIR)/xxx_defconfig"
	@echo "  make savedefconfig     Save current config as minimal defconfig"
	@echo "  make mrproper          Remove generated files (.config, headers, etc.)"

menuconfig:
	@python3 $(TOOLS_DIR)/run_menuconfig.py \
		-k $(KCONFIG_ROOT) \
		-c $(CONFIG_FILE) \
		-H $(CONFIG_HEADER)

oldconfig:
	@python3 $(TOOLS_DIR)/oldconfig.py \
		-k $(KCONFIG_ROOT) \
		-c $(CONFIG_FILE) \
		-H $(CONFIG_HEADER)

defconfig:
	@python3 $(TOOLS_DIR)/load_defconfig.py $(DEFAULT_DEFCONFIG) \
		-k $(KCONFIG_ROOT) \
		-c $(CONFIG_FILE) \
		-H $(CONFIG_HEADER)

%_defconfig:
	@if [ -f "$(DEFCONFIG_DIR)/$@" ]; then \
		python3 $(TOOLS_DIR)/load_defconfig.py $(DEFCONFIG_DIR)/$@ \
			-k $(KCONFIG_ROOT) \
			-c $(CONFIG_FILE) \
			-H $(CONFIG_HEADER); \
	else \
		echo "Error: $(DEFCONFIG_DIR)/$@ not found"; \
		exit 1; \
	fi

savedefconfig:
	@python3 -c \
		"from kconfiglib import Kconfig; \
		k = Kconfig('$(KCONFIG_ROOT)'); \
		k.load_config('$(CONFIG_FILE)'); \
		k.write_min_config('$(DEFCONFIG_DIR)/defconfig')"
	@echo "Saved minimal defconfig to $(DEFCONFIG_DIR)/defconfig"

mrproper:
	@rm -f $(CONFIG_FILE) $(CONFIG_FILE).old
	@rm -f $(CONFIG_HEADER)
	@echo "Cleaned generated config and header files."
