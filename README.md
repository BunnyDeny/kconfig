# 🔧 Kconfig Build System

✨ 一个独立的 Kconfig 构建系统，基于 [kconfiglib](https://github.com/ulfalizer/Kconfiglib) 构建，用于将 Kconfig 配置定义转化为 `.config` 文件和 C 头文件。

---

## 💡 为什么要做这个项目？

⚡ **还在手动改头文件配置 C 项目？是时候换一种方式了。**

在嵌入式开发和 C 语言项目中，我们习惯了一个 `config.h` 走天下——改个 buffer 大小，注释掉某行 `#define`，拉个新分支适配另一块板子。项目简单时还好，一旦模块变多、硬件平台变多、可选项相互牵连，手动维护头文件就变成了定时炸弹 💣：

- 😵 忘记开启某个依赖项，编译到一半撒手不管
- 🤯 数值范围完全靠开发者自律，写下 `#define PRIORITY 999` 也没人拦
- 📝 每个开发者都得熟读源码才知道有哪些配置项、默认值是多少
- 🔀 换块板子就得改头文件，一不小心就合入冲突

这正是 Linux 内核早在 2002 年就引入 **Kconfig** 解决掉的问题，也是 RT-Thread 等国产 RTOS 采用的同款方案。

### 🎯 Kconfig 能给你什么？

| 痛点 | Kconfig 的解法 |
|------|---------------|
| 🔗 选项相互依赖 | `depends on` — 关闭父项，子项自动隐藏 |
| 🔘 多选一 | `choice` — 编译器、架构、策略一目了然 |
| 🔢 数值越界 | `range` — 菜单里就拦住了，根本写不进 `.config` |
| 📖 自文档化 | `help` — 光标按 `?` 就能看到每个选项的说明 |
| 🎛️ TUI 界面 | `make menuconfig` — 不用翻头文件，空格键搞定一切 |
| 💾 多套配置 | 每种板子一个 `defconfig`，`make xxx_defconfig` 秒切 |

### 🧩 这个项目做了什么？

Linux 内核的 Kconfig 系统与内核构建深度耦合，RT-Thread 的 Kconfig 也绑在 RT-Thread 工具链上。本项目把它们中**最核心的配置→头文件转化流程**抽离出来，变成一个 **零依赖（只需 kconfiglib）、随时可嵌入任何 C 项目** 的独立工具集。

> 🗜️ 四个 Python 脚本 + 一个模板 Makefile = 你的项目立刻拥有 Linux 内核级别的配置系统。

---

## 📦 环境要求

- 🐍 Python 3.8+
- 📚 kconfiglib（包含 `menuconfig` 交互式 TUI）

### 🚀 安装 kconfiglib

```bash
# Debian / Ubuntu 🐧
sudo apt install python3-kconfiglib

# 或者通过 pip 📦
pip3 install kconfiglib
```

### ✅ 验证安装

```bash
python3 -c "from kconfiglib import Kconfig; from menuconfig import menuconfig; print('OK')"
```

看到 `OK` 就说明装好了 🎉

---

## 🏃 快速开始

```bash
git clone https://github.com/BunnyDeny/kconfig.git
cd kconfig

# 启动交互式 TUI 配置界面 🎛️
make menuconfig

# 或者直接加载预设的 defconfig ⚡
make defconfig
```

无论哪种方式，你都会得到：
- 📄 `.config` — 键值对格式的完整配置
- 🧾 `include/kconfig.h` — 带有 `#define` 宏的 C 头文件

> 🔍 默认行为：`CONFIG_FOO=y` → `#define FOO 1`（自动剥离 `CONFIG_` 前缀）

---

## 🎯 Makefile 目标一览

| 🏷️ 目标 | 📝 说明 |
|----------|---------|
| `make menuconfig` | 🎛️ 启动交互式 TUI 配置界面 |
| `make defconfig` | ⚡ 加载默认 defconfig → 生成 `.config` → 生成头文件 |
| `make xxx_defconfig` | 📂 加载 `$(DEFCONFIG_DIR)/xxx_defconfig` |
| `make oldconfig` | 🔄 将已有 `.config` 与新符号的默认值合并 |
| `make savedefconfig` | 💾 将当前 `.config` 导出为最小 defconfig |
| `make mrproper` | 🧹 清理 `.config`、`.config.old` 和生成的头文件 |

---

## ⚙️ 配置变量详解

在你的 Makefile 中覆盖这些变量，或者通过命令行传入，以适配你的项目结构：

```makefile
# 🌲 Kconfig 根文件路径（通常用 source 引入子 Kconfig）
KCONFIG_ROOT    ?= Kconfig

# 📄 生成的 .config 文件路径
CONFIG_FILE     ?= .config

# 🧾 生成的 C 头文件路径
CONFIG_HEADER   ?= include/kconfig.h

# 📂 defconfig 文件存放目录
DEFCONFIG_DIR   ?= configs

# 🎯 `make defconfig` 默认加载的 defconfig（相对路径）
DEFAULT_DEFCONFIG ?= $(DEFCONFIG_DIR)/example_defconfig

# 🔤 设为 --keep-prefix 则在 C 宏中保留 CONFIG_ 前缀
# 默认空（剥离前缀：CONFIG_FOO=y → #define FOO 1）
HEADER_KEEP_PREFIX ?=
```

### 🔍 各变量详解

#### 🌲 `KCONFIG_ROOT`
顶层 Kconfig 文件路径。这个文件通常用 `source` 指令汇总各个子系统的 Kconfig 文件（例如 `source "src/Kconfig"`）。kconfiglib 解析这一整棵树来构建符号数据库。
```
KCONFIG_ROOT := path/to/my/Kconfig
```

#### 📄 `CONFIG_FILE`
完整配置的保存位置。kconfiglib 会把每个符号及其当前值都写入这个文件。它既是配置流程的输入，也是输出。
```
CONFIG_FILE := build/.config
```

#### 🧾 `CONFIG_HEADER`
生成的 C 头文件路径。你的 C/C++ 源码 `#include` 这个头文件就能以预处理宏的形式读取配置值。

⚠️ **默认行为**：`CONFIG_` 前缀会被剥离。即 `CONFIG_MAX_TASKS=32` → `#define MAX_TASKS 32`。
如果想保留前缀，见下方的 [`HEADER_KEEP_PREFIX`](#-header_keep_prefix)。

```
CONFIG_HEADER := build/include/generated/kconfig.h
```

#### 📂 `DEFCONFIG_DIR`
存放 defconfig 文件的目录。defconfig 是一种**最小差异配置**——它只记录与符号默认值不同的条目，非常精简。

`make xxx_defconfig` 会自动到这个目录下查找：
```bash
make stm32f4_defconfig   # → 加载 configs/stm32f4_defconfig
make qemu_defconfig      # → 加载 configs/qemu_defconfig
```

```
DEFCONFIG_DIR := boards
```

#### 🎯 `DEFAULT_DEFCONFIG`
当你直接执行 `make defconfig`（不指定名称）时，加载哪个 defconfig。
```
DEFAULT_DEFCONFIG := $(DEFCONFIG_DIR)/stm32f4_defconfig
```

#### 🔤 `HEADER_KEEP_PREFIX`
默认情况下，系统会剥离 `CONFIG_` 前缀。如果你的旧代码库已经大量使用 `CONFIG_` 命名规范，可以开启这个选项：

```makefile
HEADER_KEEP_PREFIX := --keep-prefix
```

效果对比：

| `.config` | 默认（空） | `--keep-prefix` |
|-----------|-----------|-----------------|
| `CONFIG_FOO=y` | `#define FOO 1` | `#define CONFIG_FOO 1` |
| `CONFIG_BAR=42` | `#define BAR 42` | `#define CONFIG_BAR 42` |

---

## 🔌 集成到你的项目

把 `tools/` 目录和 `Makefile` 放入你的项目，然后按需定制：

```makefile
# 在你的项目 Makefile 中，include 本系统的 Makefile：
KCONFIG_ROOT    := Kconfig
CONFIG_FILE     := build/.config
CONFIG_HEADER   := build/include/kconfig.h
DEFCONFIG_DIR   := boards
DEFAULT_DEFCONFIG := $(DEFCONFIG_DIR)/stm32f4_defconfig

include kconfig/Makefile
```

或者直接把内容拷贝过去，调整路径适配你的项目结构 🧩

---

## ✍️ 编写 Kconfig 文件

仓库中的示例 `Kconfig` 是一个完整演示。核心语法速览：

```kconfig
# 🎚️ 布尔开关
config MY_OPTION
    bool "启用某某功能"
    default y
    help
      在 menuconfig 帮助面板中显示的描述文字。

# 🔢 数值配置
config MY_VALUE
    int "一个数值"
    range 0 1024
    default 256

# 🔘 单选
choice
    prompt "选择一项"
    default OPTION_A

config OPTION_A
    bool "选项 A"

config OPTION_B
    bool "选项 B"
endchoice
```

用 `source "path/to/other/Kconfig"` 将大型配置拆分到多个文件中 📁

---

## 📜 License

MIT
