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
- 🔨 GNU Make（Linux 系统自带，macOS 通过 Xcode CLT 或 `brew install make` 获得）
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

## 🎯 命令详解

### 🎛️ `make menuconfig`

打开一个蓝底白字的交互式 TUI 界面，你可以用方向键浏览、空格键勾选、`?` 查看帮助。界面会从 `Kconfig` 文件中自动生成菜单层级——不需要看源码就能了解所有可配置项。

配置完成后保存退出，系统会自动生成 `.config` 和 `include/kconfig.h`。未做修改时直接退出，做过修改会有保存提示。

### ⚡ `make defconfig`

快速恢复到某套预设配置。默认加载 `$(DEFAULT_DEFCONFIG)`（即 `configs/example_defconfig`），你也可以通过 `DEFAULT_DEFCONFIG` 变量改它。

流程：**全量重置所有符号为默认值** → 应用 defconfig 中的差异条目 → 写入 `.config` → 生成头文件。

> ⚠️ 这会**覆盖**你当前的 `.config`，旧配置全部丢失。想保留旧配置请先用 `make savedefconfig` 存一份。

### 📂 `make xxx_defconfig` ⭐ 重点

这是日常开发中最常用的命令——**一套 defconfig = 一块板子 / 一种工作模式**。

#### 🗂️ 文件必须在哪里？

defconfig 文件**必须放在 `configs/` 目录下**（或者你通过 `DEFCONFIG_DIR` 指定的目录），别无他处。系统会去 `configs/` 里查找对应的文件：

```bash
make stm32f4_defconfig   # 查找 configs/stm32f4_defconfig ✅
make qemu_defconfig      # 查找 configs/qemu_defconfig   ✅
make some/config         # ❌ 不行，不支持子目录路径
```

#### 🔄 增量还是覆盖？

**覆盖。**`make xxx_defconfig` 的行为是"全量重置再应用"：

1. 🧹 所有配置符号重置为 `Kconfig` 中定义的默认值
2. 📝 读入 defconfig 文件中的差异条目，覆写对应符号
3. 💾 写入 `.config`（完整配置）
4. 🧾 生成 `include/kconfig.h` 头文件

如果你手动改了 `.config` 之后又跑了一次 `make xxx_defconfig`，手动改动会**全部丢失**，不会保留。

```bash
# 典型工作流
git clone https://github.com/your/project.git
cd project
make stm32f4_defconfig   # 一键配置好这块板子的所有选项
make menuconfig          # 如有需要，微调几个选项
make                     # 编译
```

#### 🎯 和 `make menuconfig` 怎么配合？

- `make xxx_defconfig` → 选择"配置模板"（板级 / 模式级）
- `make menuconfig`  → 在模板基础上"微调"
- `make oldconfig`   → Kconfig 新增了选项时，补上默认值

### 🔄 `make oldconfig`

当你更新了 `Kconfig` 文件（比如新增了一个 `config NEW_OPTION`）但不想重头配置一遍时，用这个命令。

它会读取你现有的 `.config`，保留所有已有选项的值，只对**新增的符号**填入其默认值。不会覆盖或丢失任何现存配置。

> 适合升级场景：拉了个新版本代码，Kconfig 多了几个选项，跑一下 `make oldconfig` 就行。

### 💾 `make savedefconfig`

把当前 `.config` 导出为一个**最小差异 defconfig**——只保存那些和你 Kconfig 默认值不同的条目，非常精简。文件生成在 `configs/defconfig`。

```bash
make menuconfig       # 调好配置
make savedefconfig    # 保存为 configs/defconfig
mv configs/defconfig configs/myboard_defconfig  # 改个名
```

### 🧹 `make mrproper`

彻底清理，删除所有生成物：
- `.config`
- `.config.old`
- `include/kconfig.h`（以及你用 `CONFIG_HEADER` 指定的头文件路径）

> 名字来自 Linux 内核传统——`mr proper` 清洁先生，比 `clean` 更干净 🧼

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
