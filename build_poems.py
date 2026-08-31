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

def too_long(paras):
    if not (2 <= len(paras) <= 12):
        return True
    for p in paras:
        if len(p) > 16:
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
                "title": title, "author": s(au), "dynasty": "唐", "paragraphs": paras
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
                "title": rhythmic, "author": s(au), "dynasty": "宋", "paragraphs": paras
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
            if paras and not too_long(paras):
                out.append({"title": s(it["title"]), "author": "佚名",
                            "dynasty": "先秦", "paragraphs": paras})
    return out

def dedupe_key(p):
    first = p["paragraphs"][0] if p["paragraphs"] else ""
    return (p["author"], first)

def main():
    print("抓取唐诗…", file=sys.stderr)
    tang = collect_tang()
    print("抓取宋词…", file=sys.stderr)
    song = collect_song()
    print("抓取诗经…", file=sys.stderr)
    shi = collect_shijing()

    poems = []
    def add(p):
        poems.append(p)

    # 合并原手选 70 首（已是简体）
    orig = json.load(open(os.path.join(ROOT, "poems_orig70.json"), encoding="utf-8"))
    for p in orig:
        add({"title": p["title"], "author": p["author"],
             "dynasty": p["dynasty"], "paragraphs": p["paragraphs"]})

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

    # 去重
    seen, uniq = set(), []
    for p in poems:
        k = dedupe_key(p)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    # 重新编号
    for i, p in enumerate(uniq, 1):
        p["id"] = i

    out_path = os.path.join(ROOT, "poems.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=0)

    from collections import Counter
    print("总篇数:", len(uniq), file=sys.stderr)
    print("朝代分布:", dict(Counter(p["dynasty"] for p in uniq)), file=sys.stderr)
    print("输出 ->", out_path, file=sys.stderr)

if __name__ == "__main__":
    main()
