# 诗词 · 亲子朗读

手机优先的古诗词展示工具，随时打开给娃读诗。纯静态、零后端、零服务器。

- 公网地址（GitHub Pages）：`https://hengjie1993-lang.github.io/poetry-reader/`
- 备用地址（CloudStudio）：`https://94c95579db704928bac803b152eb3b8b.app.workbuddy.link`

## 功能
- 顶栏搜索：标题 / 作者 / 朝代 / 正文 / 拼音，任意匹配
- 诗词卡：逐句拼音（pinyin-pro 实时生成）、可一键隐藏
- 上一首 / 随机 / 下一首 + 列表抽屉快速跳转
- 响应式排版：字号随屏幕比例自适应，安全区适配（刘海屏/微信）
- 支持「添加到主屏幕」（PWA），首次联网后弱网/离线可读

## 数据来源与许可
- 诗词正文来自 **[chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)（MIT）**：唐诗取自 `全唐诗/poet.tang.*`，宋词取自 `宋词/ci.song.*`，诗经取自 `诗经/shijing.json`。
- 全文经 opencc 繁→简转换，按「名家 + 短诗」筛选后收敛为约 500 首。
- 拼音由前端 **[pinyin-pro](https://github.com/zh-lx/pinyin-pro)（MIT）** 实时生成，未使用任何无许可数据源。
- 结论：发布内容仅含 MIT 授权的原文文本与 MIT 拼音库，许可干净。

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
修改 `build_poems.py` 中的 `TANG_AUTHORS` / `SONG_AUTHORS` / `PER_AUTHOR` 可调整收录范围。

## 部署（GitHub Pages）
代码已 push 到 `main` 分支并开启 Pages，改动后 `git push` 即自动更新。
