# -*- coding: utf-8 -*-
"""
从 chinese-poetry (MIT) 抓取并编译亲子向诗词集 poems.json。
- 全唐诗 poet.tang.*  -> 按名家白名单 + 短诗筛选
- 宋词   ci.song.*    -> 按名家白名单筛选
- 诗经   shijing.json -> 名篇筛选
全部转简体，去重，合并原手选 70 首。
拼音由前端 pinyin-pro (MIT) 实时生成，本脚本只产出 原文/作者/朝代/段落。
"""
import json, os, sys, time, urllib.request, urllib.parse
from opencc import OpenCC

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "build_cache")
os.makedirs(CACHE, exist_ok=True)
cc = OpenCC("t2s")
API = "https://api.github.com/repos/chinese-poetry/chinese-poetry/contents/"
RAW = "https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/"

TANG_AUTHORS = set("""李白 杜甫 王维 孟浩然 王之涣 王昌龄 岑参 高适 白居易 李商隐 杜牧
刘禹锡 柳宗元 贾岛 孟郊 李绅 张继 韦应物 韩愈 元稹 贺知章 张九龄 王翰 卢纶
李益 崔颢 张志和 刘长卿 常建 王建 顾况 钱起 韩翃 司空曙 陈子昂 王勃 骆宾王
杨炯 卢照邻 杜审言 宋之问 沈佺期 王湾 祖咏 裴迪 丘为 綦毋潜 储光羲 张继
皎然 李颀 王之涣 高適 刘方平 皇甫冉 权德舆 羊士谔 雍裕之 薛涛 鱼玄机""".split())

SONG_AUTHORS = set("""苏轼 李清照 辛弃疾 李煜 晏殊 欧阳修 柳永 秦观 陆游 范仲淹 王安石 岳飞
晏几道 黄庭坚 周邦彦 姜夔 张先 向子諲 张孝祥 陈亮 刘过 蒋捷 吴文英 史达祖
张炎 周密 王沂孙 文天祥 朱淑真 张抡 康与之 曾觌 叶梦得 朱敦儒 张元干 陈与义
贺铸 毛滂 晁补之 晁冲之 舒亶 李之仪 王安国 万俟咏 曹组 周紫芝 赵佶 李邴""".split())

SHIJING_TITLES = set("关雎 蒹葭 子衿 采薇 鹿鸣 静女 硕鼠 氓 七月 伐檀 无衣 柏舟 载驰 野有蔓草 击鼓 桃夭 芣苢 汉广 摽有梅 绸缪".split())

PER_AUTHOR = 14  # 每位作者最多保留首数

def fetch_json(path):
    # 简单磁盘缓存，便于重复运行
    fn = os.path.join(CACHE, path.replace("/", "_").replace(":", "_"))
    if os.path.exists(fn):
        with open(fn, "r", encoding="utf-8") as f:
            return json.load(f)
    url = RAW + urllib.parse.quote(path)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "poetry-build"})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode("utf-8"))
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            return data
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
    return None

def s(t):
    if not t:
        return ""
    return cc.convert(t)

def norm_line(p):
    return p.strip()

# 部分生僻字位于 CJK 扩展区（扩展 A/B/C/D/E），常见手机系统字体缺字会显示成
# 豆腐块（空白）。统一替换为 CJK 基本区的通行字，保证绝大多数设备可正常显示。
CLEAN_MAP = {
    '\U0002C907': '諲',  # 向子諲（原为扩展 E 区异体字）
    '\u4360':      '篱', # 接篱（白接篱，头巾）
    '\U0002B5E7': '餗',  # 饪餗
    '\U0002B40C': '輧',  # 朱輧（车）
    '\U0002CD0A': '驎',  # 骐驎（同麒麟）
    '\U00023A3C': '殢',  # 须殢（沉溺）
}

def clean_text(t):
    if not t:
        return ""
    return ''.join(CLEAN_MAP.get(c, c) for c in t)

def too_long(paras, max_line=16):
    # 唐诗/宋词短句每行通常 ≤16 字；诗经是四言两句式，单行可达 ~20 字，
    # 故诗经收集器传 max_line=24，其余体裁保持 16 以免长诗混入。
    if not (2 <= len(paras) <= 12):
        return True
    for p in paras:
        if len(p) > max_line:
            return True
    return False

def collect_tang():
    out = {}
    for n in range(0, 45000, 1000):
        d = fetch_json(f"全唐诗/poet.tang.{n}.json")
        if not d:
            continue
        for it in d:
            au = it.get("author", "")
            if au not in TANG_AUTHORS:
                continue
            paras = [norm_line(s(x)) for x in it.get("paragraphs", []) if x and x.strip()]
            title = s(it.get("title", "")).strip()
            if not title or not paras or too_long(paras):
                continue
            out.setdefault(au, []).append({
                "title": title, "author": s(au), "dynasty": "唐",
                "genre": "诗", "paragraphs": paras
            })
    return out

def collect_song():
    out = {}
    for n in range(0, 30000, 1000):
        d = fetch_json(f"宋词/ci.song.{n}.json")
        if not d:
            continue
        for it in d:
            au = it.get("author", "")
            if au not in SONG_AUTHORS:
                continue
            paras = [norm_line(s(x)) for x in it.get("paragraphs", []) if x and x.strip()]
            rhythmic = s(it.get("rhythmic", "")).strip()
            if not rhythmic or not paras or too_long(paras):
                continue
            out.setdefault(au, []).append({
                "title": rhythmic, "author": s(au), "dynasty": "宋",
                "genre": "词", "paragraphs": paras
            })
    return out

def collect_shijing():
    d = fetch_json("诗经/shijing.json")
    out = []
    if not d:
        return out
    for it in d:
        if it.get("title", "") in SHIJING_TITLES:
            paras = [norm_line(s(x)) for x in it.get("content", []) if x and x.strip()]
            # 诗经 content 有的按句、有的按章存储，单行长度参差；对儿童朗读而言
            # 「章数 ≤12」才是合理门槛，单行长度放宽到 60（整章会自然换行显示）。
            if paras and not too_long(paras, max_line=60):
                out.append({"title": s(it["title"]), "author": "佚名",
                            "dynasty": "先秦", "genre": "诗经", "paragraphs": paras})
    return out

def collect_yuanqu():
    """元曲（小令/短章）。yuanqu.json 含杂剧与散曲，用 too_long 仅收短小令。"""
    d = fetch_json("元曲/yuanqu.json")
    out = {}
    if not d:
        return out
    for it in d:
        au = it.get("author", "")
        if not au:
            continue
        paras = [norm_line(s(x)) for x in it.get("paragraphs", []) if x and x.strip()]
        title = s(it.get("title", "")).strip()
        if not title or not paras or too_long(paras):
            continue
        out.setdefault(au, []).append({
            "title": title, "author": s(au), "dynasty": "元",
            "genre": "曲", "paragraphs": paras
        })
    return out

def collect_chuci():
    """楚辞（屈宋诸篇），content 为诗句数组。先秦。"""
    d = fetch_json("楚辞/chuci.json")
    out = {}
    if not d:
        return out
    for it in d:
        au = it.get("author", "") or "佚名"
        content = it.get("content", []) or it.get("paragraphs", [])
        paras = [norm_line(s(x)) for x in content if x and x.strip()]
        title = s(it.get("title", "")).strip()
        if not title or not paras or too_long(paras):
            continue
        out.setdefault(au, []).append({
            "title": title, "author": s(au), "dynasty": "先秦",
            "genre": "楚辞", "paragraphs": paras
        })
    return out

def collect_nalan():
    """纳兰性德词集，字段为 para（非 paragraphs）。清。"""
    d = fetch_json("纳兰性德/纳兰性德诗集.json")
    out = {}
    if not d:
        return out
    for it in d:
        au = it.get("author", "") or "纳兰性德"
        paras = [norm_line(s(x)) for x in it.get("para", []) if x and x.strip()]
        title = s(it.get("title", "")).strip()
        if not title or not paras or too_long(paras):
            continue
        out.setdefault(au, []).append({
            "title": title, "author": s(au), "dynasty": "清",
            "genre": "词", "paragraphs": paras
        })
    return out

def collect_caocao():
    """曹操诗集，仅 title/paragraphs 两字段，作者统一为曹操。汉。"""
    d = fetch_json("曹操诗集/caocao.json")
    out = {}
    if not d:
        return out
    for it in d:
        paras = [norm_line(s(x)) for x in it.get("paragraphs", []) if x and x.strip()]
        title = s(it.get("title", "")).strip()
        if not title or not paras or too_long(paras):
            continue
        out.setdefault("曹操", []).append({
            "title": title, "author": "曹操", "dynasty": "汉",
            "genre": "诗", "paragraphs": paras
        })
    return out

def dedupe_key(p):
    first = p["paragraphs"][0] if p["paragraphs"] else ""
    return (p["author"], first)

def guess_genre(dyn):
    return {"唐": "诗", "宋": "词", "先秦": "诗经", "汉": "诗",
            "元": "曲", "清": "词", "明": "诗"}.get(dyn, "诗")

def main():
    print("抓取唐诗…", file=sys.stderr)
    tang = collect_tang()
    print("抓取宋词…", file=sys.stderr)
    song = collect_song()
    print("抓取诗经…", file=sys.stderr)
    shi = collect_shijing()
    print("抓取元曲…", file=sys.stderr)
    yuan = collect_yuanqu()
    print("抓取楚辞…", file=sys.stderr)
    chu = collect_chuci()
    print("抓取纳兰词…", file=sys.stderr)
    nalan = collect_nalan()
    print("抓取曹操诗…", file=sys.stderr)
    cao = collect_caocao()

    poems = []
    def add(p):
        poems.append(p)

    # 合并原手选 70 首（已是简体）
    orig = json.load(open(os.path.join(ROOT, "poems_orig70.json"), encoding="utf-8"))
    for p in orig:
        add({"title": p["title"], "author": p["author"],
             "dynasty": p["dynasty"], "genre": guess_genre(p.get("dynasty", "")),
             "paragraphs": p["paragraphs"]})

    for au, lst in tang.items():
        lst.sort(key=lambda x: (len(x["paragraphs"]), sum(len(p) for p in x["paragraphs"])))
        for p in lst[:PER_AUTHOR]:
            add(p)
    for au, lst in song.items():
        lst.sort(key=lambda x: (len(x["paragraphs"]), sum(len(p) for p in x["paragraphs"])))
        for p in lst[:PER_AUTHOR]:
            add(p)
    for p in shi:
        add(p)
    for au, lst in yuan.items():
        lst.sort(key=lambda x: (len(x["paragraphs"]), sum(len(p) for p in x["paragraphs"])))
        for p in lst[:PER_AUTHOR]:
            add(p)
    for au, lst in chu.items():
        lst.sort(key=lambda x: (len(x["paragraphs"]), sum(len(p) for p in x["paragraphs"])))
        for p in lst[:PER_AUTHOR]:
            add(p)
    for au, lst in nalan.items():
        lst.sort(key=lambda x: (len(x["paragraphs"]), sum(len(p) for p in x["paragraphs"])))
        for p in lst[:PER_AUTHOR]:
            add(p)
    for p in cao.get("曹操", []):
        add(p)

    # 去重
    seen, uniq = set(), []
    for p in poems:
        k = dedupe_key(p)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    # 兜底：缺失体裁的条目按朝代推断补齐
    for p in uniq:
        if not p.get("genre"):
            p["genre"] = guess_genre(p.get("dynasty", ""))

    # 重新编号
    for i, p in enumerate(uniq, 1):
        p["id"] = i

    # 清洗扩展区生僻字（保证移动端可显示，避免豆腐块）
    for p in uniq:
        p["title"] = clean_text(p["title"])
        p["author"] = clean_text(p["author"])
        p["dynasty"] = clean_text(p["dynasty"])
        p["paragraphs"] = [clean_text(x) for x in p["paragraphs"]]

    out_path = os.path.join(ROOT, "poems.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=0)

    from collections import Counter
    print("总篇数:", len(uniq), file=sys.stderr)
    print("朝代分布:", dict(Counter(p["dynasty"] for p in uniq)), file=sys.stderr)
    print("输出 ->", out_path, file=sys.stderr)

if __name__ == "__main__":
    main()
