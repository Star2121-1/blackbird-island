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
# distribute；docs/development.md 的"出包"一节写了完整命令行（那份不进发行包，
# 根目录的 README 是给玩家看的）。出完把 zip 拆开看过再算完成。
# ============================================================

init python:
    build.name = "blackbird"
    # 输出目录钉死。默认值是 "{directory_name}-dists"，而 directory_name 里带版本号——
    # 以前 config.version 从没生效（options.txt 是死文件），包就落在 blackbird-dists/；
    # 把 version 补成 1.0 的下一次出包直接改写到 blackbird-1.0-dists/ 去了，
    # 旧目录原封不动躺在那儿，审计脚本对着五个过期包报 all good。
    build.destination = "blackbird-dists"

    build.classify("game/99_shots.rpy*", None)
    build.classify("game/saves/**", None)
    build.classify("game/cache/**", None)
    build.classify("shots/**", None)
    build.classify("tools/**", None)
    build.classify("**/__pycache__/**", None)
    build.classify("**~", None)
    build.classify("**.bak", None)
    build.classify("**.orig", None)

    # 全量源字体是裁字表的原料，游戏用的是 game/fonts/ 里的子集（0.5MB×5），
    # 授权文本也已经在 build_fonts.py 里落到 game/fonts/LICENSE-*.txt 了，
    # 所以整个 fonts_src/ 都不用进包（里面只剩一张字表 glyphs.txt 和源许可原件）。
    # 提醒：分类成 None 的整目录会让打包器不再往里走——想在这条之后再"放行"
    # 其中的文件是没有用的，实测过。要放行就得排在它前面。
    build.classify("fonts_src/**", None)
    # docs/ 里是开发说明，通篇讲"终稿不点名""第八个名字怎么拼都不对"。
    # 根目录那份 README 才是给玩家的。这条不写，开发说明会以普通数据文件的
    # 身份混进发行包——build.documentation("*.md") 只管根目录那一层。
    build.classify("docs/**", None)
    # 开发机上长出来的三样：崩溃回显、运行日志、tools/ 的依赖表。
    # requirements.txt 讲的是怎么在新机器上跑 tools/，而 tools/ 本身不进包，
    # 留着只会让看包的人多一个不明白的文件。
    build.classify("log.txt", None)
    build.classify("traceback.txt", None)
    build.classify("requirements.txt", None)

    build.documentation("*.md")
    build.documentation("LICENSE*")
