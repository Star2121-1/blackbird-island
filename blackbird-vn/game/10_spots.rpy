# ============================================================
# 热点内容：第一日至第五日
# 每个 spot_<id> 由 bb_search 调起，看完回到调查界面。
# 措辞取自《黑鸟岛-终稿》对应章节，只删不增。
# ============================================================


# ---------------- 第一日 · 补 ----------------
label spot_wettrail:
    N "那滴水渍我又跟了一遍。从书房过来，到纸片这里断掉——回去的那一条，没有。"
    $ ev_give("wet_trail")
    return

label spot_photos:
    N "纸袋放回暗格之前，我把没念出来的那两张又看了一遍。"
    N "第二张是桥下的礁石，第三张是礁石旁的草丛。两张都是空镜，没有人。"
    N "桥、礁石、草丛、蹲着的人——拍的人是照着这个顺序走过来的。"
    $ ev_give("photos")
    return

label spot_cigarette:
    N "矮木几上两只烟灰痕。他掐灭的时候手指很稳。"
    N "烟灰落在袖口上，他没有管。"
    $ ev_give("cigarette")
    return


# ---------------- 第二日 ----------------
label spot_records:
    N "东翼那道门是被撬开的。门缝里搁着一只牛皮纸袋，袋口没有扎。"
    N "一年一叠。每一叠上是三样东西：一个名字，一个现场，一个记号。"
    N "赵寒的父亲记了不止一年。"
    $ ev_give("watch_badge")
    $ ev_give("east_wing_records")
    return

label spot_cups:
    N "八只杯我又数了一遍，还是七满一空。这一次要记的是那只空杯的年头。"
    N "从八仙桌摆进大厅那天早上起，就没有人给那只续过水。之后的每一清早，也没有。"
    $ ev_give("cup_empty")
    return

label spot_sheet:
    N "桌角一页黄纸，边缘磨得起毛，折成四折。"
    N "二〇〇九年临东海勘查记录的一页。位置C。"
    N "昨天散场前它还折回四折收在桌下抽屉里。今天回到了桌上。谁开的抽屉，没有人说破。"
    $ ev_give("pos_c_sheet")
    return


# ---------------- 第三日 ----------------
label spot_mark:
    N "一张便签。没有字。只画了一个记号——盾形，交叉的钥匙，盾底下一道波浪线。"
    N "那道门楣，人人都从下面走。它偏偏留在这里，留给会认得它的人。"
    N "我认得它。"
    $ ev_give("door_mark")
    return

label spot_handbook:
    N "我把那几页又看了一遍。空白。"
    N "我不记得那天夜里我有没有写下过什么。也不记得，我到底，有没有在。"
    $ ev_give("handbook_blank")
    return

label spot_plaque:
    N "中间那一张，是立牌的记录。"
    N "一个名字，一个现场，一个记号。落款只有一个字。"
    N "陈。"
    N "不是陈建国。"
    $ ev_give("plaque_record")
    return

label spot_blank:
    N "右边那一张，我翻过来看。"
    N "背面，一个字也没有。"
    N "留下这一张的人，把名字空掉了。"
    $ ev_give("blank_sheet")
    return

label spot_face:
    N "那张脸摊在桌上，正对空杯。刚才大厅里人人都看过了，我不再写一遍。"
    N "我记住的是背面那两个字的笔画：写得很用力，末笔拖出去了一点。"
    $ ev_give("face_photo")
    return


# ---------------- 第四日 ----------------
# 封装记录那一段原先在这儿（spot_seal）。第四日正文里林晚已经把那张纸放到桌角
# 并且说了那三条，证据也在那一处 ev_give；这个热点就成了没人调的死内容，删。
label spot_blankcol:
    N "那张摊开的纸，第三条底下还有一格。"
    N "格子上印着两个字：复核人。"
    N "二〇〇九年，这一栏是空的。没有填。"
    N "方廷用两根手指点了点它。他说，一栏空白有两种可能。"
    $ ev_give("blank_col")
    return

label spot_erased:
    N "第八个名字，被墨擦掉了。擦的顺序，自下而上。那不是污渍，是一个书写动作。"
    N "擦掉的痕迹上，残着一个偏旁。半个字。陈。"
    N "苏蔓拍过那张名单。墨擦的痕迹，在照片里。她比我们更早看见了这件事。"
    $ ev_give("erased8_photo")
    return

label spot_cable:
    N "退潮以后能看见那条沟。沿礁石埋着的信号缆，线皮磨毛了，一绞就断。"
    N "断口是新的。从那天起，黑鸟岛和大陆，再无连接。"
    N "一通电话，都打不出去了。八个人。"
    $ ev_give("cable_cut")
    return


# ---------------- 第五日 ----------------
label spot_rope:
    N "小艇的缆绳，是从旧缆桩上解开的。没有人提这件事。"
    N "他没有出岛。傍晚缆绳还是解开的样子。"
    $ ev_give("rope_stale")
    return

label spot_cupmark:
    N "杯收走了。桌上多了一截浅白的纸。"
    N "纸没有写字，只压出一个浅淡的杯印。"
    $ ev_give("cup_mark")
    return

label spot_notehand:
    N "苏蔓对照过周亦安的册子。那张纸条与“陈是守望者之一”那一行，同一只手。"
    $ ev_give("note_hand")
    return

label spot_lockhalf:
    N "后半夜停电，林晚去东翼换保险丝。"
    N "那道赵寒撬开以后新换的锁，向左移了半寸。钉是弯的，门板上有一道弧形磨痕。"
    N "我摸了一下柄。柄是凉的。"
    $ ev_give("lock_half")
    return
