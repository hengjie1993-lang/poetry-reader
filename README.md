# 小诗囊 · 亲子朗读

手机优先的古诗词展示工具，随时打开给娃读诗。纯静态、零后端、零服务器。

> 名字取自唐代诗人李贺「锦囊觅句」的典故——古人随身带囊收存诗稿。「囊」即口袋，正合装在手机里随手取用的形态；加一「小」字，是给孩子的小口袋。

- 公网地址（GitHub Pages）：`https://hengjie1993-lang.github.io/poetry-reader/`
- 上手前建议阅读 `HANDOFF.md`（项目交接手册：改动铁律、核心算法、踩坑清单）

## 功能
- 顶栏搜索：标题 / 作者 / 朝代 / 正文 / 拼音，任意匹配
- 诗词卡：逐字拼音（pinyin-pro 实时生成，标点粘附前字）、可一键隐藏
- 上一首 / 随机 / 下一首 + 列表抽屉快速跳转
- 响应式排版：字号随屏幕比例自适应，安全区适配（刘海屏/微信）
- 手机端按标点小句分行，段落（上/下阕）之间留更大间距；宽屏保持整句自然换行
- 支持「添加到主屏幕」（PWA），首次联网后弱网/离线可读

## 数据来源与许可
- 诗词正文来自 **[chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)（MIT）**：
  - 唐诗 `全唐诗/poet.tang.*`、宋词 `宋词/ci.song.*`、诗经 `诗经/shijing.json`
  - 元曲 `元曲/yuanqu.json`、楚辞 `楚辞/chuci.json`、纳兰性德词集、曹操诗集
- 全文经 opencc 繁→简转换，按「名家 + 短诗」筛选后收敛为 **1500 首**，覆盖 **唐 / 宋 / 元 / 清 / 汉 / 先秦** 六朝，体裁含 **诗 / 词 / 曲 / 楚辞 / 诗经**。
- 拼音由前端 **[pinyin-pro](https://github.com/zh-lx/pinyin-pro)（MIT）** 实时生成，未使用任何无许可数据源。
- 结论：发布内容仅含 MIT 授权的原文文本与 MIT 拼音库，许可干净。
- 本项目代码同样以 **MIT** 发布，详见 [LICENSE](LICENSE)。

## 本地预览
```bash
cd 项目目录
python -m http.server 8090
# 浏览器打开 http://localhost:8090  （不要用 file:// 直接双击）
```

## 扩充 / 重新生成数据
```bash
pip install opencc-python-reimplemented
python build_poems.py      # 抓取并编译 -> poems.json
git add poems.json && git commit -m "data: 更新诗词集" && git push
```
修改 `build_poems.py` 中的 `TANG_AUTHORS` / `SONG_AUTHORS` / `PER_AUTHOR` 或新增的 `collect_yuanqu/collect_chuci/collect_nalan/collect_caocao` 收集器，可调整收录范围。

## 部署（GitHub Pages）
代码已 push 到 `main` 分支并开启 Pages，改动后 `git push` 即自动更新。
