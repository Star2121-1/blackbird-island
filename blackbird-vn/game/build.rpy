# ============================================================
# 打包规则。发行包里不该有的东西：
#   99_shots——BB_SHOT=1 的截图后门，正常流程进不去，但 label 还在包里；
#   saves／cache——各平台自己会生成；
#   tools／fonts_src／shots——开发用的脚本、16MB 全量字体原料、截图产物；
#   编辑器留下的 .bak／~ 与 __pycache__。
#
# 两条从实测里学到的，别按直觉改：
#   1. 后写的规则覆盖先写的（00build.rpy 把 base_patterns 一路 append，
#      解析时后匹配者胜）。所以"排除一大片、再放行其中几个"要按这个顺序写。
#   2. 只写 game/99_shots.rpy 挡不住它——打包时同名的 .rpyc 会被另一条默认
#      规则收进来。第一次出包就在 zip 里看见了 99_shots.rpyc。用 .rpy*。
#
# 出包命令不是 `renpy <proj> dist`（引擎没有这个命令），要走 launcher 注册的
# distribute；README 的"出包"一节写了完整命令行。出完把 zip 拆开看过再算完成。
# ============================================================

init python:
    build.name = "blackbird"

    build.classify("game/99_shots.rpy*", None)
    build.classify("game/saves/**", None)
    build.classify("game/cache/**", None)
    build.classify("shots/**", None)
    build.classify("tools/**", None)
    build.classify("**/__pycache__/**", None)
    build.classify("**~", None)
    build.classify("**.bak", None)
    build.classify("**.orig", None)

    # 全量源字体是裁字表的原料，游戏用的是 game/fonts/ 里的子集（0.5MB×5）。
    # 只挡字体二进制，不挡 fonts_src/ 整目录：挡整目录的话打包器根本不再往里走，
    # 后面那条"放行 LICENSE"就没有机会命中——实测少掉了授权文本。
    build.classify("fonts_src/**.ttf", None)
    build.classify("fonts_src/**.otf", None)

    build.documentation("*.md")
    build.documentation("LICENSE*")
