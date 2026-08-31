# 诗词 · 亲子朗读（静态版 v1）

一个零后端、零部署的手机/电脑古诗词展示工具，专为「随时打开、给孩子读诗」设计。

## 特点
- 单页静态站点，不依赖任何服务器、数据库。
- 手机优先、响应式；电脑上自动居中铺宽。
- 拼音用 MIT 协议的 `pinyin-pro` 在浏览器端实时生成，逐句标注，方便念准多音字。
- 简易搜索：按 标题 / 作者 / 朝代 / 正文 / 拼音 过滤。
- 上一首 / 下一首 / 随机 切换，列表抽屉快速跳转。
- 支持「加到主屏幕」(PWA)：首次联网打开后，弱网/离线也能看。

## 目录
- `index.html` —— 前端页面（Vue3 + 自写 CSS，无 Element Plus 依赖）
- `poems.json` —— 精选诗词集（v1 共 70 首，含唐40/宋24/元明清汉若干）
- `manifest.webmanifest` / `sw.js` —— PWA 配置与离线缓存
- `import_chinese_poetry.py` —— 从 Chinese-poetry 批量扩充词库的脚本（可选）

## 本地预览
```bash
cd poetry-reader
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```
> 注意：不要直接双击 `index.html`（file:// 协议下 fetch 会被浏览器拦截）。
> 拼音需要联网加载一次 `pinyin-pro` CDN；之后浏览器会缓存。

## 发布到 GitHub Pages（获得稳定链接）
1. 在 GitHub 新建一个仓库（如 `poetry-reader`），把本目录全部文件推上去。
2. 仓库 Settings → Pages → Source 选 `main` 分支根目录 → Save。
3. 几分钟后获得 `https://<用户名>.github.io/poetry-reader/` 链接。
4. 把链接发到微信「文件传输助手」，在微信里打开 → 右上角「···」→「浮窗」，
   以后从微信浮窗入口秒开；或浏览器书签保存。

## 扩充诗库
直接编辑 `poems.json`，按现有结构追加即可：
```json
{ "id": 71, "title": "题目", "author": "作者", "dynasty": "唐", "paragraphs": ["第一句。", "第二句。"] }
```
拼音会自动生成，无需手动加。
需要一次性从 GitHub 开源库 `chinese-poetry` 批量导入并转简体、注音，可运行
`import_chinese_poetry.py`（见脚本内说明）。

## 版权说明
- 诗词文本属公有领域；本项目的精选、排版为原创整理。
- 拼音由 MIT 协议的 `pinyin-pro` 生成，可自由使用。
- 如后续需要「译文/注释」，建议从个人使用角度引用，切勿整体再分发无协议来源（如 poetry-md）。
