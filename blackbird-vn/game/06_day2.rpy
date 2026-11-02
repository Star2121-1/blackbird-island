# ============================================================
# 流程层：第二日（十一月十八日）
#   第七章 绣标 → 第八章 东翼 → 第九章 摆好的尸体
# 台词取自《黑鸟岛-终稿》第七至九章，措辞不改，只删不增。
# 顾言笙 2025 笔记只作日与日之间的呼吸口，插在第七章开头两句。
# ============================================================


# ---------------- 第七章：绣标 ----------------
label ch7:
    call screen bb_card("第七章", "绣标", "袖口里缝着一枚守望者的绣标。", "十一月十八日", BB_SNAP("bg_hall_long.jpg"))
    scene bg_hangzhou
    show spr_gu as talker at bb_talk_r
    # 终稿 1340–1348：这一页笔记是"陈"从一个签名变成一个身份的唯一现场。
    # 不演它，第十八章苏蔓那句"陈是守望者之一那一行，同一只手"、尾声那条批注、
    # 第四轮那一处 reveal 全都在引一句玩家没见过的话。
    GU "我去翻那份手抄小册子的最后一页。"
    GU "最后一页，只有一行字，墨迹很淡，像是刻意要被人看见之前抹去的样子——陈是守望者之一。陈在位置C。"
    GU "又是这个陈。这次，它有了一个身份——守望者。"
    GU "我忽然明白了一件事：我一直在找陈是谁，却从来没有想过，陈可能不是一个名字，而是两代人。"
    GU "窗外的雨没有停。"
    scene bg_hall_long
    show spr_me as talker at bb_talk_r
    ME "天亮的时候，我睡不着。"
    ME "我确定我姓陈。我确定我叫陈默。"
    ME "我确定我在杭州住过——或者，我记不清了。"
    ME "我确定我有一张身份证，照片上是这张脸。"
    N "王剑回来了。"
    N "他袖口里揣着一个油布包。约拳头大小，麻线缠着，是从旧缆桩上解下来的。"
    N "他在炉火边把它点燃。纸的边角先黑，一圈一圈往里烧。"
    show spr_wang as talker at bb_talk_r
    WANG "不该被我们八个人看见的东西。"
    N "最先开口的是周亦安。"
    N "他手里拿着第四张照片——那张蹲着的人的照片。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "我们昨晚都在意照片里的人是谁。但都漏了一个细节。"
    N "他用放大镜对准连帽衫的袖口。"
    ZHOU "这里有一个绣标。昨晚你们没看清，因为光线太暗。我刚才补拍了。"
    N "放大后的绣标很清楚——是一个盾形徽章，里面有一把交叉的钥匙和一条波浪线。"
    show spr_su as talker at bb_talk_r
    SU "这是什么？"
    show spr_zhou as talker at bb_talk_r
    ZHOU "一个自称守望者的组织。二十年前，临海市，有几个年轻人成立过这样一个团体，专门做一件事——"
    N "周亦安，取出一册子。旧的，薄的，边角翻毛了。"
    ZHOU "这是我早年，手抄的。守望者的每一个符号。"
    N "他翻开。封皮内页，缝着一枚绣标——和袖口上那一枚，一样。"
    $ ev_give("watch_badge")
    show spr_me as talker at bb_talk_r
    ME "做什么？"
    show spr_zhou as talker at bb_talk_r
    ZHOU "给死人立牌。"
    ZHOU "那些被定性为意外、疾病、不明的死亡，他们会在现场留一个记号。一个只有他们自己看得懂的记号。"
    show spr_lin as talker at bb_talk_r
    LIN "位置C。"
    LIN "十二米。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "对。"
    ZHOU "那不是警方的勘查编号，是他们的记号。位置C，距撞击点十二米。"
    ZHOU "守望者把C读作correspondence——被对应。意思是有人把它对应到另一起死亡上。"
    ZHOU "有人把一具尸体摆在位置C，好让它看起来属于那场车祸。"
    N "大厅里静得能听见海浪。"
    show spr_lin as talker at bb_talk_r
    LIN "先杀后撞。"
    LIN "和我父亲当年尸检初稿里写的，是一回事。"
    show spr_su as talker at bb_talk_r
    SU "他去哪了？"
    show spr_lin as talker at bb_talk_r
    LIN "他凌晨两点去过东翼。"
    LIN "我起夜，在走廊的灯下，看见他的影子从东翼那扇被封的门后头出来了。"
    show spr_me as talker at bb_talk_r
    ME "东翼？"
    ME "那不是封住了吗？"
    show spr_lin as talker at bb_talk_r
    LIN "封住了。"
    LIN "门上那道锁，是我们上岛那天换的，不是旧锁。他没用钥匙，用的是工具。"
    LIN "持续了二十秒上下。"
    N "我看向那扇通往东翼的门。锁孔里有一圈细密的金属摩擦痕——那是一根开锁工具反复拨动留下的，不是一下带过的。"
    N "赵寒在找什么。他要去一个封住的房间，开锁的手法熟练得让人心里发毛。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "我们到现在，还在替赵寒问他为什么。但真正该问的是——"
    ZHOU "——他打算让我们看见，还是打算让我们永远不知道。"
    jump ch8


# ---------------- 第八章：东翼 ----------------
label ch8:
    call screen bb_card("第八章", "东翼", "东翼不是档案室，是我待的地方。", "十一月十八日", BB_SNAP("bg_hall_ring.jpg"))
    scene bg_hall_ring
    N "天亮的时候，赵寒回来了。"
    N "他站在大厅正中，没有坐下。一只手垂在身侧，指缝里夹着一小截被撕下来的纸角。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "东翼，我撬开了。"
    N "新锁被撬开之后，他没有复位。它吊在那里。"
    ZHAO "两点。新锁，我换了工具。二十秒上下。"
    show spr_me as talker at bb_talk_r
    ME "里面是什么？"
    N "赵寒没有回答。"
    N "他从大衣内袋里取出一个牛皮纸袋，放在矮木几上。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "不是一张。是立牌的记录。一张纸上，一个名字，一个现场，一个记号。一年一叠，摞了一摞。"
    show spr_su as talker at bb_talk_r
    SU "为什么留在那扇门后？"
    show spr_zhao as talker at bb_talk_r
    ZHAO "那一头统共一间房。我站在门口，一眼就数完了。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "整栋庄园，他只封了这一间。封了二十年。一间房，值得一个人封二十年。"
    N "大厅里静了几秒。"
    N "沈南舟出现了。他从楼梯下来，脚步声很轻，几乎听不见。"
    show spr_shen as talker at bb_talk_r
    SHEN "诸位。"
    SHEN "赵先生，那叠东西——拆，或者不拆，我都不拦。"
    scene bg_east_wing
    SHEN "东翼不是档案室。是我一个人待的地方。每年，我回来，待一夜。"
    scene bg_hall_ring
    show spr_su as talker at bb_talk_r
    SU "待一夜做什么？"
    show spr_shen as talker at bb_talk_r
    SHEN "守。"
    SHEN "有些东西，该有人守着。我父亲那一代，是守着这些的。"
    show spr_su as talker at bb_talk_r
    SU "那为什么是岛上？"
    show spr_shen as talker at bb_talk_r
    SHEN "临海那边的东西，得运到一个临海的人想不到的地方。沈家三代做航运。黑鸟岛，是我们家的冬仓。"
    N "这句话落地的时候，我看见王剑的手动了一下。"
    show spr_wang as talker at bb_talk_r
    WANG "二〇一三。"
    WANG "那年，你也在？"
    N "沈南舟没有否认，也没有承认。"
    show spr_shen as talker at bb_talk_r
    SHEN "你们认得那叠里的哪一年？"
    show spr_wang as talker at bb_talk_r
    WANG "我认得二〇一三。那年我立过一块。"
    $ ev_give("plaque_2013")
    N "大厅里更静了。"
    N "赵寒走到纸袋前，把它翻开。二〇〇九那一叠搁在最上面。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "这一叠，我留了。"
    show spr_me as talker at bb_talk_r
    ME "为什么？"
    show spr_zhao as talker at bb_talk_r
    ZHAO "二〇〇九。"
    ZHAO "我父亲查的就是这一年。查到一半，他停手了。剩下那一半，我接了下来。"
    show spr_me as talker at bb_talk_r
    ME "那一半，是什么？"
    N "赵寒没有回答。"
    N "他看着我，眼底那圈青黑，像很久没有合过眼。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "我不知道。"
    N "这四个字从他嘴里出来，分量很重。我认得这种语气——那不是承认，是拒绝。"
    # 终稿第八章东翼这一段（1467–1479）是赵寒"那一半"的对手方：沈南舟亲口承认他父亲
    # 当年不是查不出来，是查到了东翼里的一样东西，而且那样东西现在还在东翼。
    # 不演这一段，第四轮他那句"我父亲查到的那一半，我记下来了"就只是一个人的说法。
    # 位置必须在 ch8：纸袋在这一章才摊开着，第九章散场时它已经收走了。
    show spr_shen as talker at bb_talk_r
    SHEN "但你父亲当年停在那一步，不是因为查不出来。"
    SHEN "他查到了东翼里的一样东西。"
    SHEN "查到它，就没有回头。"
    N "赵寒的手停在纸袋上。他看了沈南舟很久。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "一样东西，"
    ZHAO "你替我父亲留着，就别再还给他。他收不下了。"
    show spr_shen as talker at bb_talk_r
    SHEN "它一直在东翼。"
    N "他转过身，理了理袖口，看着东翼那扇门的方向，没有再说话。"
    N "从那一夜起，我的记忆不再连成整片。我记得什么，就写什么。这段文字不是记录，是筛子。"
    jump ch9


# ---------------- 第九章：摆好的尸体 ----------------
label ch9:
    call screen bb_card("第九章", "摆好的尸体", "八只杯，一只空着，自始至终没人碰。", "十一月十八日", BB_SNAP("bg_hall_table.jpg"))
    scene bg_hall_table
    N "我进大厅的时候，刚过九点。环形沙发撤掉了，换成一张八仙桌。"
    N "桌上摆着八只杯。名单上，八个名字，一人一只。"
    N "七只满着的，正着放；空的那只，倒扣在正对门的位置。"
    N "杯，是仆从每清早摆的。那只倒扣的，摆上去，就是倒扣的。"
    N "沈南舟站在桌后，没有坐。"
    show spr_shen as talker at bb_talk_r
    SHEN "诸位，"
    SHEN "请坐。"
    SHEN "王先生，"
    SHEN "这一场，得有您，才算齐。"
    N "周亦安把一样东西放在桌上。一张纸，折成四折，展开，是二〇〇九年临东海勘查记录的一页。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "那一页，该还回档案馆的，没有还。"
    ZHOU "在座的人，都记得十一月十七，晚上十点四十七。"
    ZHOU "一辆黑色轿车，在临东海大桥西侧的匝道上，撞了一个行人。"
    ZHOU "官方的口径，四个字。"
    ZHOU "当场死亡。"
    ZHOU "林晚。"
    show spr_lin as talker at bb_talk_r
    LIN "我父亲那一版的死亡时间，九到十时。"
    show spr_fang as talker at bb_talk_r
    FANG "九到十时。"
    FANG "在十点四十七之前。"
    show spr_lin as talker at bb_talk_r
    LIN "是。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "一个人，如果最迟在十点，已经死了——他在十点四十七被一辆车撞到的那一刻，撞之前，他不是活人。"
    ZHOU "被撞的那个行人，不是被撞上的。"
    N "是被摆在那里的。"
    ZHOU "一个把死人摆进车辙里的人，装在心里的是下一个来看这件现场的人。摆，是摆给谁看。"
    show spr_fang as talker at bb_talk_r
    FANG "一个死后被移动、被放进车辙里的人，和一个活着的人被车撞倒，不是同一类事实。"
    FANG "是伪造一个现场。"
    FANG "需要一个在场的人，让那个现场，成立。"
    N "王剑在门口，盯着那张纸。他没有看苏蔓。"
    show spr_wang as talker at bb_talk_r
    WANG "二〇一三。"
    WANG "那叠里，我立过的那一块。"
    show spr_su as talker at bb_talk_r
    SU "一个肇事的人，回来，给别人的死立一块。"
    SU "你想记住，还是想钉死谁？"
    show spr_wang as talker at bb_talk_r
    WANG "那辆车，"
    WANG "是我开的。"
    WANG "我写的是目击者。那三个字，是我写的。"
    show spr_me as talker at bb_talk_r
    ME "我没有接话。我看见了这句话落下去之后的东西——那辆车确实是他开的，可被撞的人，在那一刻之前，已经死了。承认开车，不等于，杀了谁。"
    N "我盯着王剑。有一瞬间，我几乎要以为，是陈默替我，把这句话接住的。"
    ME "不是我的记忆。我记不清了。"
    N "沈南舟收起那张纸，折回四折。他折得很慢，像一个把一件事做完的人。"
    show spr_shen as talker at bb_talk_r
    SHEN "今天到这里。"
    SHEN "赵先生，二〇〇九那一叠，我不动它。你若要带走，我让人备一只箱子。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "不走了。"
    N "半句。"
    ZHAO "让该知道的人，知道。"
    N "他没有说，该知道的人，是谁。"
    # 终稿 1639：那张勘查页今晚就是在这里进的抽屉。不写这一句，
    # 第三日"它回到了桌上。谁开的抽屉，没有人说破"就没有前件，
    # 而当日那一格搜索也只能把纸写在桌上——桌上此刻已经没有纸了。
    N "沈南舟没有追问。他把折好的纸放进桌下的抽屉里，抽屉合上时，发出一声很轻的响。"
    N "那只空着的杯子，自始至终，没有人去碰。"
    call bb_search("bg_hall_table", "八仙桌 · 今天到这里", TABLE_SPOTS_D2)
    N "杯子收回去了。规则没有收回：举起一条证据，抵在一句话上。"
    call bb_debate_run(round2)
    call bb_result_card(round2)
    jump day2_pass
