# 《黑鸟岛：筛子》

长篇推理小说《黑鸟岛》的视觉小说改编，全本：序章 + 二十四章 + 尾声，六天一夜读完的一份卷宗。

```
序章 2025·杭州（顾言笙翻开手稿）
  第一日  ch1 抵达 → ch2 → ch3 书房（第八个名字）→ ch4 → ch5 → ch6 大厅 · 第一轮
  第二日  ch7 → ch8 → ch9 → 八仙桌 · 第二轮
  第三日  ch10 → ch11 → ch12 → ch13 → 大厅 · 第三轮
  第四日  ch14 → ch15 → ch16 → 大厅 · 第四轮
  第五日  ch17 → ch18 → ch19 → 大厅 · 第五轮
  第六日  ch20 → ch21 → ch22 → ch23 → ch24 → 合上卷宗
尾声 2025·杭州
```

每天夜里合上手稿，回到市档案馆的阅览室，读一段顾言笙的调查笔记（`game/12_days.rpy`）。

## 玩的方式和弹丸论破不一样

弹丸论破的圆桌裁决奖励"指出凶手"。这本书的地基是不可知——终稿不点名。
所以本作的胜利条件是 **逼出多少沉默**：把一条证据抵在一句话上，让说话的人停下来。

- 五轮对质，合计 40 句话（7／9／8／8／8），留了破绽的是 2／3／3／3／3 句——
  全六日一共 14 处沉默可逼。打到几处算几处。
- 反驳机会：第一轮 3 次（教学局），往后每夜 4 次——多给一次，错一次还有余地。
- 失败不改变真相，只改变收尾那几句话。
- 沈南舟那一格是"反问"，不算赢：主人不会沉默，他把问题推回你手上。
- 死亡时间在第三句才到手，却要用在第二句上：一圈听完会自动回到第一句，
  桌上写"第 2 遍在听"。也可以直接点名牌跳回某个人重听。
- 第八个名字在第三章被读到（"我没有看清"），在第十四章正面出现时给玩家拼——
  那是**反谜题**：无论怎么拼都拿不到，一律回"我没有看清"。
  这一屏是在教玩家——这本书不让你指认谁。

## 基调：界面就是那份卷宗

不是"游戏套一层纸的皮"。玩家翻的是手稿本身，岛上的照片是夹进卷宗的现场快照。

- 纸面 `#eae5da` 是唯一的阅读面；深色照片只当场景，字一律落在纸上。
- 牛皮纸底纹压 0.22：再深就把 20px 的小字一起压到 2.5:1 以下了。

颜色各有专司，不许串：

| 色 | 用途 |
| --- | --- |
| 墨 `#0b0d10` | 中性的一切，包括说话人的名字 |
| 锈 `#b5342a` | **只**给"一个人被问到停下来"和红头栏／密级章 |
| 金 `#7a5f0e` `#c9a227` | 手里握着的证据、正在发言的那一席 |
| 冷蓝 `#33505f` | 沈南舟的反问 |
| 铅笔灰 | 顾言笙（2025 笔记层）与一切元信息 |

悬停反馈一律走形状（下划线／位移），不走颜色。状态另有非颜色的冗余编码
（涂黑条、虚线框、回形针、装订孔），图例见游戏内"怎么读这份卷宗"。

## 跑起来

需要 [Ren'Py 8.x](https://www.renpy.org/latest.html)。

```
renpy.exe blackbird-vn          # 打开项目
renpy.exe blackbird-vn lint     # 静态检查
renpy.exe blackbird-vn compile  # 编译
```

素材缺位也能跑：`game/04_images.rpy` 里每个图像都有纯色占位，
`game/images/` 下出现同名文件就自动换成真图。

## 文件

| 文件 | 作用 |
| --- | --- |
| `game/00_settings.rpy` | 设计令牌（色／字号／纸面）、样式、角色 |
| `game/01_data.rpy` | 证据表、圆桌发言、座位、拼字数据、`Debate` 逻辑 |
| `game/02_screens.rpy` | 全部界面。交互统一 `call screen → _return → label 改状态` |
| `game/03_flow.rpy` | 序章、第一日、热点内容、对质与结算的调用点 |
| `game/04_images.rpy` | 图像注册（真图 / 占位二选一） |
| `game/05_day1_gap.rpy` … `game/09_day5.rpy` | 第一至第五日正文 |
| `game/10_spots.rpy` | 各日热点内容（取证在这里进证据栏） |
| `game/11_day6.rpy` | 第六日 ch20–ch24 |
| `game/12_days.rpy` | 日与日之间的 2025 笔记。两套日历在这里交手：扉页写岛上的日子（十一月十七日起），笔记是二〇二五年的，每段笔记场景重盖一次 `bb_day`，否则菜单里的"日期"会挂着岛上那天，读起来像本子记错了日子 |
| `game/13_rounds_ab.rpy` | 第二轮、第三轮发言表 |
| `game/14_rounds_cd.rpy` | 第四轮、第五轮发言表 |
| `game/build.rpy` | 打包规则：截图屏／存档／缓存不进发行包 |
| `game/99_shots.rpy` | 无头截图自检（临时屏，不参与正常流程；由 `build.rpy` 排除出包） |
| `tools/build_assets.py` | 素材清洗：背景裁 1920×1080，立绘自适应抠品红底＋去溢色＋底边渐隐 |
| `tools/build_ui_assets.py` | PIL 画界面硬件：桌环、席位点、规则线、图钉、回形针、装订孔、角章 |
| `tools/build_fonts.py` | 从 `fonts_src/` 的全量 Noto Sans CJK 裁出本作字表，写回 `game/fonts/`（16MB → 0.5MB）；顺带把 OFL 授权文本从源字体 name 表里取出来并排放好 |
| `tools/build_icon.py` | 用静默章拼出 `game/icon.ico` 和 `game/icon.png`；窗口图标用 png（pygame 读不了 ico 里 256 那条 PNG 压缩项），ico 留给 Windows 可执行文件 |
| `tools/check_fonts.py` | 缺字闸门：`game/*.rpy` 里每个字都必须在对应字体 cmap 里，缺了就渲染成空白 |
| `tools/check_verbatim.py` | 改编不变量：台词逐字可溯 + 三条体例 |
| `tools/test_content.py` | 跨文件完整性：证据有没有孤儿、破绽证据当晚拿不拿得到、热点有没有死标签、每句有没有落空时的话、报了日期的笔记有没有重盖 `bb_day` |
| `tools/make_contact.py` | 把 `shots/` 拼成一张联络表，方便一次看全 |
| `tools/test_logic.py` | 不启 Ren'Py，直接跑 `01_data.rpy` 里的对质逻辑 |

## 自检

没有测试员，所以留了几条机器能跑的检查：

```
python tools/test_logic.py          # 逻辑：反驳／沉默／循环／拼字
python tools/test_content.py        # 跨文件完整性与公平性
python tools/check_verbatim.py      # 改编不变量
python tools/check_fonts.py         # 缺字（改完文案必须重跑）
renpy.exe blackbird-vn lint         # 语法与未引用图像
cd blackbird-vn && rm -f shots/*.png && RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1 BB_SHOT_DIR=shots renpy.exe .
python tools/make_contact.py 4      # shots/_contact.png
cd blackbird-vn && RENPY_SKIP_MAIN_MENU=1 BB_AUTOPLAY=1 renpy.exe .   # 全六日无点击跑通，stdout 应只有 [AUTO] 行
```

改了文案要先重跑 `python tools/build_fonts.py` 再跑 `check_fonts.py`：
裁剪出来的字表是静态的，新字渲染成空白而不报错。

截图脚本只用 `show screen` + `pause`，不产生需要点击的交互。唯一例外是确认框：
`modal` 的屏会把 `pause` 自己的超时事件吃掉（它压在 modal 下面），两者互锁、脚本挂住——
所以版面单独抽成不带 modal 的 `bb_confirm_panel`，`19_confirm` 截那一层。
无头截图出来是 994×559，不是 1920×1080：量的是相对位置，不是像素。

## 出包

引擎本身没有 `dist` 这个命令——打包是 launcher 项目注册的 `distribute`：

```
renpy.exe <SDK 目录> distribute --no-update <本项目绝对路径>
```

产出在上一级的 `blackbird-dists/`：pc／win／mac／linux 四个包加一个 market 包。
单个平台约 50MB，其中 40MB 是 Ren'Py 运行时（两个 dll）。
`game/99_shots.rpy*`、`tools/`、`shots/`、整个 `fonts_src/` 由 `build.rpy` 排除，
OFL 授权文本不依赖 `fonts_src/`——`build_fonts.py` 已经把它落到 `game/fonts/LICENSE-*.txt`，
跟着子集字体一起进包。
出完包要把 zip 的目录列出来核对，别只相信规则写上了——第一次就漏了
`99_shots.rpyc`（规则只写了 `.rpy`）。另外记着：分类成 `None` 的整目录会让打包器
不再往里走，排在它后面的"放行"规则轮不到，所以放行要写在排除前面。

## 台词纪律

每一句台词、每一条圆桌发言都取自 `../黑鸟岛-终稿.md`，只做删节，不做增写。
新增内容一律标在旁白位（`N`），不放进任何角色的嘴里。

例外只有界面本身要说的话：序章、尾声、过场笔记、热点描述，以及数据层里的
`hit`／`miss` 旁白。台词行若确实需要自撰，行尾标 `# 自撰`，校验器会把它算进
"界面自撰"而不是"找不到出处"。

终稿是 markdown，直引号 `"…"` 用得多；界面一律排成 `“…”`。这是排版不是措辞，
校验器两边都剥掉引号再比。
