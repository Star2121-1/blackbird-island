# ============================================================
# 第四日（十一月二十日）：第十四章 名单 → 第十五章 见证 → 第十六章 空栏
# 台词取自《黑鸟岛-终稿》第十四至十六章，措辞不改，只删不增。
# 第十四章是枢纽：被擦掉的第八个名字在这里正面出现。
# 第十四章是枢纽：被擦掉的第八个名字在这里正面出现，接 `call hangman_8`。
# ============================================================


# ---------------- 第十四章：名单 ----------------
label ch14:
    call screen bb_card("第十四章", "名单", "第八个名字，被墨擦掉了。", "十一月二十日", BB_SNAP("bg_hall_table.jpg"))
    scene bg_hall_table
    N "雾退了一整夜。"
    N "十一月二十日，清晨。大厅里，那张脸还搁在桌上，正对那只空杯。没有人动它。"
    N "林晚把卷宗里那张封装记录放在桌角。"
    show spr_lin as talker at bb_talk_r
    LIN "位置C的异物，只记了三条。一，发现。二，位置。三，封装人。"
    LIN "没有第四条。"
    N "大厅里，没有人出声。"
    LIN "三条。别的，没有记。"
    N "她合上那张纸。她把它收回大衣口袋。动作很慢，像在收一份尸检报告。"
    N "我把这个数记住了。三。"
    $ ev_give("seal_rec")
    scene bg_study
    N "清晨，我又去了趟书房，把那份名单从桌上抽出来。"
    N "当时，我的目光停在陈默。名单上最后一个名字，我没有看清。"
    N "这次，我直接看了。"
    N "名单上的八个名字。岛上七个。"
    N "最后一个名字，我没看清。"
    call hangman_8
    N "擦掉它的人，不想让人看见那个名字。"
    N "擦掉的痕迹上，残着一个偏旁。半个字。"
    N "陈。"
    N "苏蔓拍过那张名单。我刚才看了她的手机。"
    call bb_search("bg_study", "书房 · 名单与照片", STUDY_SPOTS_D4)
    jump ch15


# ---------------- 第十五章：见证 ----------------
label ch15:
    call screen bb_card("第十五章", "见证", "复核这件事，本身，就是一次到场。", "十一月二十日", BB_SNAP("bg_hall_table.jpg"))
    scene bg_hall_table
    N "大厅里，雾快散了。赵寒站了起来。他没有看任何人。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "我父亲查到的那一半，我记下来了。"
    N "他从内袋取出一张对折的纸。摊开。折痕裂了一声。他把它压平，按在桌沿上。"
    N "位置C。封装记录。第三条，封装人。"
    ZHAO "上面，本来该有第四条。复核人。"
    N "大厅里没有人说话。"
    ZHAO "二〇〇九年，这一栏是空的。没有填。"
    N "苏蔓看着他。"
    show spr_su as talker at bb_talk_r
    SU "空着，是因为查不到，还是因为不能写？"
    N "赵寒没有接。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "我父亲追的，是那个复核人是谁。他停手，是因为那个名字，他认得。"
    ZHAO "认得，又不能写出来的，那种。"
    N "大厅里静了很久。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "二〇一三。"
    N "周亦安开口。"
    ZHOU "一个复核人，如果就是后来回来给那一块立过牌的那一个——复核这件事，本身，就是一次到场。"
    N "王剑坐在那里，没有动。"
    show spr_su as talker at bb_talk_r
    SU "王剑，你二〇一三回来，给那一块立过牌。"
    N "苏蔓开口。她转向我。"
    SU "还有一个人，二〇〇九在位置C核过复。你，核过复吗？"
    N "我没有回答。"
    show spr_shen as talker at bb_talk_r
    N "沈南舟从那一头走了过来。他站在那张摊开的纸旁边，没有看它。"
    SHEN "先生，复核人那一栏，我父亲那一代，是留着的。"
    N "他没有说“留着”是什么意思。"
    scene bg_study
    N "夜里来了一阵风暴，雨水漫进了庄园西翼。苏蔓那晚在台灯下核名单，台灯坏了，她移到西翼那侧的窗边。手机就搁在纸页旁。"
    N "清晨，它开了机，照片却大多打不开了。屏幕闪了两下，停在相册上。名单的照片，在那部手机里。"
    show spr_su as talker at bb_talk_r
    SU "还能打开的，只有两张。名单。还有那个绣标——周亦安补拍的那一张，我存过。"
    N "那阵风暴，还绞断了沿礁石埋着的那根信号缆——埋得浅，线皮磨毛了。一绞，就断了。岛上与外界唯一的连接，断了。从那天起，黑鸟岛和大陆，再无连接。"
    scene bg_hall_table
    N "没有人多问一句。外面什么时候会注意到，没有人说得清。"
    SU "一通电话，都打不出去了。八个人。"
    call bb_search("bg_shore", "礁石 · 退潮之后", SHORE_SPOTS_D4)
    scene bg_hall_table
    N "雾散尽了。大厅里，只剩那一张摊开的纸，和那一栏空的。"
    call bb_search("bg_hall_table", "大厅 · 摊开的那张纸", TABLE_SPOTS_D4)
    jump ch16


# ---------------- 第十六章：空栏 ----------------
label ch16:
    call screen bb_card("第十六章", "空栏", "一栏空白，有两种可能。", "十一月二十日", BB_SNAP("bg_hall_table.jpg"))
    scene bg_hall_table
    N "大厅里，雾散尽了。日头落进窗里。"
    show spr_fang as talker at bb_talk_r
    N "方廷终于开了口。他站起来，走到桌前，用两根手指，点了点那一栏空白。"
    FANG "一栏空白，有两种可能。一，没人填。"
    N "他停了停。"
    FANG "二，有人填了，又把名字抹掉了。"
    N "大厅里很静。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "哪种，更像故意的。"
    N "周亦安接上。"
    ZHOU "一个复核的人，如果只想留证据，不留自己——他会把名字空掉。"
    show spr_su as talker at bb_talk_r
    N "苏蔓转向我。"
    SU "你认得那个把名字空掉的人吗？"
    ME "我不知道。"
    show spr_fang as talker at bb_talk_r
    N "方廷接上。"
    FANG "留证据，不留名，这一栏就不成立。"
    FANG "它需要一个愿意署名的人，来补。"
    show spr_zhao as talker at bb_talk_r
    N "赵寒走过去，站在那张纸前。"
    ZHAO "我父亲留着的，就是这一栏。他补不了。"
    N "我没有接话。"
    scene bg_study
    N "那张纸在日头里，空着那一栏，像一道没有底的缺口。"
    scene bg_hall_table
    N "赵寒忽然直起身。"
    ZHAO "十二米。我在桥的照片上数的。十八步。"
    ZHAO "摆一具尸体，要三十秒。数，是我父亲的报告里写的。剩下的至少四十六分半，他没有离开桥。"
    # 这一条是赵寒亲口报出来的数，当场就进证据栏；只作卷宗深度，五轮都不用它抵人。
    $ ev_give("bridge_count")
    show spr_shen as talker at bb_talk_r
    N "沈南舟站在那儿，没有看那张纸。他看着我。"
    SHEN "先生，有些名字，是不能补上去的。"
    N "他没有说为什么。"
    N "日头落尽之前，桌上摆开第四遍。规则还是那一条：举起一条证据，抵在一句话上。"
    call bb_debate_run(round4)
    call bb_result_card(round4)
    jump day4_pass
