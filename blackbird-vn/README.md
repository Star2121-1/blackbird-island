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

- 五轮对质，每轮 8～9 句话，其中只有 3～4 句留了破绽。打到几处算几处。
- 反驳机会：第一轮 3 次（教学局），往后每夜 4 次——多给一次，错一次还有余地。
- 失败不改变真相，只改变收尾那几句话。
- 沈南舟那一格是"反问"，不算赢：主人不会沉默，他把问题推回你手上。
- 听完一轮可以点座位回到某个人身上重听。
- 第三章的第八个名字是**反谜题**：无论怎么拼都拿不到，一律回"我没有看清"。
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
| `game/12_days.rpy` | 日与日之间的 2025 笔记 |
| `game/13_rounds_ab.rpy` | 第二轮、第三轮发言表 |
| `game/14_rounds_cd.rpy` | 第四轮、第五轮发言表 |
| `game/99_shots.rpy` | 无头截图自检（临时屏，不参与正常流程，发布前删） |
| `tools/build_assets.py` | 素材清洗：背景裁 1920×1080，立绘自适应抠品红底＋去溢色＋底边渐隐 |
| `tools/build_ui_assets.py` | PIL 画界面硬件：桌环、席位点、规则线、图钉、回形针、勾选框 |
| `tools/build_fonts.py` | 从 `fonts_src/` 的全量 Noto Sans CJK 裁出本作字表，写回 `game/fonts/`（16MB → 0.5MB） |
| `tools/check_verbatim.py` | 改编不变量：台词逐字可溯 + 三条体例 |
| `tools/make_contact.py` | 把 `shots/` 拼成一张联络表，方便一次看全 |
| `tools/test_logic.py` | 不启 Ren'Py，直接跑 `01_data.rpy` 里的对质逻辑 |

## 自检

没有测试员，所以留了几条机器能跑的检查：

```
python tools/test_logic.py                                      # 逻辑
python tools/check_verbatim.py                                  # 改编不变量
renpy.exe blackbird-vn lint                                     # 语法
cd blackbird-vn/tools && python -c "import build_ui_assets as b; b.build_table(); b.build_hardware()"
rm -f shots/*.png && RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1 BB_SHOT_DIR=shots renpy.exe .
python tools/make_contact.py 3                                  # shots/_contact.png
```

截图脚本只用 `show screen` + `pause`，不产生需要点击的交互。
`bb_gallery` / `bb_settings` 是 modal 屏幕，`show screen` 配 `pause` 会互锁，抓不到——
这两个面板只能手工开一次看。
无头截图出来是 994×559，不是 1920×1080：量的是相对位置，不是像素。

## 台词纪律

每一句台词、每一条圆桌发言都取自 `../黑鸟岛-终稿.md`，只做删节，不做增写。
新增内容一律标在旁白位（`N`），不放进任何角色的嘴里。

例外只有界面本身要说的话：序章、尾声、过场笔记、热点描述，以及数据层里的
`hit`／`miss` 旁白。台词行若确实需要自撰，行尾标 `# 自撰`，校验器会把它算进
"界面自撰"而不是"找不到出处"。

终稿是 markdown，直引号 `"…"` 用得多；界面一律排成 `“…”`。这是排版不是措辞，
校验器两边都剥掉引号再比。
