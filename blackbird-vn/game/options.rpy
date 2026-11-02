# ============================================================
# 游戏信息。这个文件以前叫 options.txt，而 Ren'Py 只读 .rpy——
# 那份 txt 从来没生效过：窗口标题取的是目录名，关于页的"版本 "后面是空的，
# 存档目录退化成"解压出来叫什么就叫什么"（renpy.py 的 path_to_saves：
# save_directory 为 None 时用 gamedir 的上一级名字）。玩家把文件夹改名或
# 换一层目录，存档就"丢"了。
#
# 8.5.3 的 config 里没有 url／about 这两个变量（写上去 lint 直接报
# "not a known configuration variable"）：项目自己的关于页在 02_screens.rpy
# 的 screen about，仓库地址在随包的 README 里。
#
# 数字改了要一起动 docs/development.md 与 tools/：沉默总数由 test_content.py
# 的闸门锁着（现在是 11），证据条数由 EVIDENCE 的长度决定。
# ============================================================

define config.name = _("黑鸟岛：筛子")
define config.version = "1.0"

# 存档目录写死，不跟着解压出来的文件夹名走。
define config.save_directory = "blackbird_island_saves"
