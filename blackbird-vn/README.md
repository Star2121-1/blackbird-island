# 黑鸟岛：筛子

一份没有结案的手稿。你扮演顾言笙，在一座渡轮只开一趟的岛上待六天。
这本书不许你指认谁——你赢的方式，是逼出多少沉默。

## 怎么开始

解压后直接运行，不需要安装：

| 平台 | 入口 |
| --- | --- |
| Windows | `blackbird.exe` |
| macOS | `blackbird.app` |
| Linux | `blackbird.sh` |

macOS 首次打开若被拦下，在「访达」里按住 Control 点应用 →「打开」。
Linux 先给启动脚本执行权限再运行：`chmod +x blackbird.sh && ./blackbird.sh`。
（包里没有叫 `blackbird` 的文件；那个名字是脚本内部启动的可执行体，不用直接碰。）

## 键位

| 键 | 作用 |
| --- | --- |
| 鼠标点击 / 空格 / 回车 | 继续下一句 |
| `Esc` | 菜单：存档、读档、设置、帮助 |
| `Ctrl` | 快进 |
| `Tab` | 跳过读过的句子（再按一次取消） |
| 方向键 + 回车 | 对质时选中证据、举起、反驳 |
| 右上角「日志」 | 回看说过的话 |
| `S` | 截图 |

游戏内按 `Esc` →「怎么读这份卷宗」有完整规则说明，第一次对质之前建议先看一眼。

## 界面说明

版面按 1920×1080 设计，所有元素留在 5% 安全区内；窗口任意缩放由引擎整体等比处理，
不会破坏对齐。设置页里没有字号和行距滑杆——全站是像素定宽的版面，字一放大图例、
证据轨、对白页就会被裁切。要看清小字请把窗口拉大或使用系统缩放。

## 存档位置

Windows：`%APPDATA%\RenPy\blackbird_island_saves`
macOS：`~/Library/RenPy/blackbird_island_saves`
Linux：`~/.renpy/blackbird_island_saves`

这一串名字写死在 `config.save_directory` 里，不跟着你把游戏解压成什么文件夹名走——
改名、挪位置，存档还在原处。

## 授权

字体为思源宋体（Noto Serif SC）、思源黑体（Noto Sans CJK SC）与马善政毛笔楷书
（MaShanZheng），均为 SIL Open Font License 1.1；每个字体的授权文本与
`OFL-1.1.txt` 随包在 `game/fonts/` 下。
音效与全部背景、纸面贴图为本项目程序化合成，无外部素材。

## 关于本作

改编自同名长篇推理小说《黑鸟岛》。游戏只做删节，不增写一句台词；
小说的结局问题——是谁——在这份手稿里同样不给答案。
