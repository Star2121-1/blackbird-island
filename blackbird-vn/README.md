# 《黑鸟岛：筛子》Ren'Py 垂直切片

长篇推理小说《黑鸟岛》的视觉小说改编。第一版只做 10–15 分钟的切片：

```
序章 2025·杭州（顾言笙翻开手稿）
  → 第一章 抵达（码头／大厅，点击取证）
  → 第三章 书房（取证 + 第八个名字）
  → 第六章 大厅第一轮（圆桌对质）
  → 结算（沉默计数）
```

## 玩的方式和弹丸论破不一样

弹丸论破的圆桌裁决奖励"指出凶手"。这本书的地基是不可知——终稿不点名。
所以本作的胜利条件是 **逼出多少沉默**：把一条证据抵在一句话上，让说话的人停下来。

- 第一轮有 7 句话，其中只有 2 句留了破绽。打到几处算几处。
- 失败不改变真相，只改变收尾那几句话。
- 沈南舟那一格是"反问"，不算赢：主人不会沉默，他把问题推回你手上。
- 反驳机会 3 次。用完就进结算。听完一轮可以点座位回到某个人身上重听。
- 第三章的第八个名字是**反谜题**：无论怎么拼都拿不到，一律回"我没有看清"。
  这一屏是在教玩家——这本书不让你指认谁。第十四章它会以另一种方式回来。

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
| `game/00_settings.rpy` | 字体、配色（墨／雾／锈红）、样式、角色 |
| `game/01_data.rpy` | 证据、圆桌发言、座位、拼字数据 |
| `game/02_screens.rpy` | 全部界面。交互统一 `call screen → _return → label 改状态` |
| `game/03_flow.rpy` | 剧本流程与台词 |
| `game/04_images.rpy` | 图像注册（真图 / 占位二选一） |
| `game/99_shots.rpy` | 无头截图自检（临时屏，不参与正常流程） |
| `tools/build_assets.py` | 素材清洗管线：背景裁 1920×1080，立绘自适应抠品红底＋去溢色＋底边渐隐 |
| `tools/build_fonts.py` | 从 `fonts_src/` 的全量 Noto Sans CJK 裁出本作字表，写回 `game/fonts/`（16MB → 0.5MB） |
| `tools/test_logic.py` | 不启 Ren'Py，直接跑 `01_data.rpy` 里的对质逻辑，22 项断言 |

## 自检

没有测试员，所以留了三条机器能跑的检查：

```
python tools/test_logic.py                                      # 逻辑
renpy.exe blackbird-vn lint                                     # 语法
RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1 renpy.exe blackbird-vn         # 逐屏截图到 shots/
```

截图脚本只用 `show screen` + `pause`，不产生需要点击的交互。
`bb_gallery` / `bb_settings` 是 modal 屏幕，`show screen` 配 `pause` 会互锁，抓不到——
这两个面板只能手工开一次看。

## 台词纪律

切片里的每一句台词都取自 `../黑鸟岛-终稿.md` 的第一、三、六章，只做删节，不做增写。
新增内容一律标在旁白位（`N`），不放进任何角色的嘴里。
