# 小诗囊 · 项目交接手册

> 面向「接手修改本项目」的 AI 工具或开发者。读完本文即可安全改动，无需重新踩坑。
> 项目地址：`D:\WorkBuddy-Results\poetry-reader`
> 线上地址：https://hengjie1993-lang.github.io/poetry-reader/
> 当前版本：**v14**（`APP_VERSION = '14'`，最后一次提交 `cdcc739`）

---

## 1. TL;DR — 改一个字要动哪些地方

| 你改了什么 | 必须同步做什么 | 不做的后果 |
|---|---|---|
| `index.html` | 把里面 `APP_VERSION` 升 1 → **并把 `sw.js` 的 `CACHE` 和 `APP_VERSION` 也升** | **手机端看不到任何改动**（这是本项目最大的坑） |
| `sw.js` | 同上，且 `CACHE` 版本号必须与 `APP_VERSION` 一致 | 同上 |
| `poems.json` | 升 `APP_VERSION`（因为数据请求带 `?v=` 版本戳） | 手机端读到旧数据 |
| 纯注释/文档 | 无需升版 | — |

**当前版本号是 14，下一个改动请升到 15。**

---

## 2. 项目概览

| 项 | 值 |
|---|---|
| 定位 | 手机优先的古诗词朗读工具，给学龄前/小学孩子读诗用 |
| 形态 | **纯静态网页，不是 App**。微信浮窗 / 浏览器书签 / 加到主屏 |
| 技术栈 | Vue 3（CDN 全局版）+ 原生 CSS，**零构建工具**（无 Vite / npm / 打包） |
| 后端 | 无。零服务器、零数据库 |
| 拼音 | 前端 pinyin-pro（MIT，CDN）**运行时实时生成**，数据文件里不存拼音 |
| 部署 | GitHub Pages（`main` 分支根目录，push 即自动发布） |
| 数据源 | chinese-poetry（MIT）经 opencc 转简 → 收敛为 500 首 |
| 许可 | 干净。正文 MIT + 拼音库 MIT，无任何无协议数据源 |

### 为什么是零构建单文件？
刻意选择。目的是让任何环境（甚至手机上的编辑器）都能直接改一行 HTML 然后推送。**如果要引入 Vite/npm，请先确认确实有必要**——当前单文件方案是优势不是技术债。

---

## 3. 文件地图

| 文件 | 作用 | 改动频率 |
|---|---|---|
| `index.html` | **全部应用代码**：模板 + 样式 + 逻辑（约 370 行） | 高 |
| `poems.json` | 诗词数据，500 首 / 113KB | 低 |
| `sw.js` | Service Worker，离线缓存。**微信内被主动禁用** | 低（但改 index 时必动） |
| `manifest.webmanifest` | PWA 配置（`name`/`short_name` 均为「小诗囊」） | 极低 |
| `build_poems.py` | 数据编译脚本：抓 chinese-poetry → 转简体 → 筛选 → 去重 | 低 |
| `poems_orig70.json` | 初版手选 70 首备份，`build_poems.py` 会合并它 | 不动 |
| `README.md` | 产品说明（给人看） | 低 |
| `PUBLISH.md` | GitHub Pages 发布清单（历史遗留，流程已稳定） | 不动 |
| `build_cache/` | 抓数据的磁盘缓存，**已被 .gitignore 忽略** | 不动 |
| `HANDOFF.md` | 本文件 | 低 |

---

## 4. 核心机制（改动前必须理解）

### 4.1 渲染管线

```
poems.json ──fetch(?v=APP_VERSION)──> this.all
                                        │
                            搜索过滤 ──> this.view
                                        │
                                   this.current（当前一首）
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
  titleBlocks                     authorBlocks                      poemLines
  buildBlocks(title)        buildBlocks('〔'+朝代+'〕'+作者)      buildBlocks(小句)
        │                               │                               │
        └───────────────────────────────┴───────────────────────────────┘
                                        │
                          char-pair 块（汉字在上，拼音在下）
```

### 4.2 拼音算法：`buildBlocks(text)` ← 全项目最核心的函数

返回 `[{char, py, isPunct}]` 数组。规则：

1. 用 `pinyinArray(text)`（`pinyin-pro` 的 `type:'array'`）一次性取整段拼音，**保留上下文**以便多音字正确（如「水调歌头」的调→diào）。
2. 逐字符配对。
3. **标点粘附到前一个汉字块**，不单独占位。
4. **行首标点先缓存，前缀给后面第一个汉字**（v12 修复点）。

```js
let prefix = '';
for(let i=0;i<chars.length;i++){
  if(isPunct(ch)){
    if(blocks.length){ blocks[blocks.length-1].char += ch; }  // 粘到前字
    else { prefix += ch; }                                     // 行首：先缓存
  }else{
    blocks.push({char: prefix + ch, py:py, isPunct:false});    // 前缀给首个汉字
    prefix = '';
  }
}
if(prefix) blocks.push({char: prefix, py:'', isPunct:true});   // 纯标点兜底
```

**效果示例**

| 输入 | 输出块 |
|---|---|
| `〔宋〕王安石` | `〔宋〕`(sòng) / 王(wáng) / 安(ān) / 石(shí) |
| `水调歌头·明月几时有` | 水 / 调(diào) / 歌 / `头·`(tóu) / 明 / 月 / 几 / 时 / 有 |
| 《静夜思》 | `《静`(jìng) / 夜(yè) / `思》`(sī) |

> ⚠️ 改这个函数时，**必须重新验证行首标点**——见 §6 坑位表 v4 / v12。

### 4.3 响应式策略：`isMobileMode`

```js
const mq = window.matchMedia('(max-width: 640px)');
```

- **手机端**：`splitClauses(para)` 按 `，。！？、；：` 切小句，**一句一行**（工整）。
- **宽屏**：整句靠 `flex-wrap` 自然换行。

段落间（如词的上/下阕）用 `paraBreak` 标记加大间距。

> 经验：**手机端按语义小句强制分行，比"自动折行"工整得多**。长句（尤其宋词长短句）用自动折行会参差不齐。

### 4.4 缓存策略（本项目历史重灾区）

| 场景 | 行为 |
|---|---|
| 微信内置浏览器（UA 含 `MicroMessenger`） | **完全禁用 SW**，并注销已有 SW。每次走网络拿最新文件 |
| 其他浏览器（Safari/Chrome） | 注册 SW，支持「添加到主屏幕」离线读 |

- `index.html` 请求数据：`fetch('poems.json?v=' + APP_VERSION)`，失败后回退 `poems.json` 裸地址。
- `sw.js` 对 `poems.json` 和 `index.html` 一律 **network-first**；其余静态资源 cache-first。
- `sw.js` 的 `fetch` 失败时返回 **503 JSON 而非 index.html**（绝不能把 HTML 当 JSON 返回，会崩）。

### 4.5 随机行为（v13 起）

- **每次打开页面 = 随机一首**，不再固定为第一首《静夜思》。
- 实现：`mounted()` 拉到 `poems.json` 后立刻调一次 `this.shuffle()`。
- 随机源 `randInt(n)`：优先 `crypto.getRandomValues`（密码学安全随机），不可用时回退 `Math.random()`。
  n=500 量级下取模偏差约 1e-7，可忽略。
- 点「随机」按钮走的是**同一个** `shuffle()`，行为一致。
- ⚠️ **首屏不是第一首属于预期行为，不是 bug**。若要改回固定起手，
  删掉 `mounted()` 里的 `this.shuffle()` 即可（`data` 中 `idx:0` 会让它回到第一首）。

---

## 5. 数据结构

`poems.json` 是一个数组，每项：

```json
{
  "id": 1,
  "title": "静夜思",
  "author": "李白",
  "dynasty": "唐",
  "paragraphs": ["床前明月光，", "疑是地上霜。", "举头望明月，", "低头思故乡。"]
}
```

- `paragraphs` 元素已含句末标点。
- 宋词的 `title` 用的是词牌名（`rhythmic` 字段）。
- 排序规则：`build_poems.py` 按 `(段落数, 总字数)` 升序，每作者最多 `PER_AUTHOR=14` 首 —— 即**优先收录短诗**，这是为亲子朗读场景服务的。

**重新生成数据**
```bash
pip install opencc-python-reimplemented
python build_poems.py
```
调收录范围改 `TANG_AUTHORS` / `SONG_AUTHORS` / `SHIJING_TITLES` / `PER_AUTHOR`。
注意：脚本会合并 `poems_orig70.json`，**别删那个文件**。

---

## 6. 踩坑清单 ⭐ 最重要的一节

按版本倒序。每一个都是真实踩过的，改动时请对照检查。

| 版本 | 现象 | 根因 | 解法 / 教训 |
|---|---|---|---|
| **v14** | 诗词正文字间距忽近忽远 | `.char-pair` 宽度由「汉字/拼音谁更宽」决定，不同拼音长度差异导致字块宽度不一 | 正文 `.line-flex .char-pair` 强制等宽 `1.6em`，汉字间距真正均匀；标点块仍保持 `auto` |
| **v13** | 每次打开都固定显示《静夜思》 | `idx` 初始 `0`，`shuffle()` 只在点按钮时触发 | `mounted()` 拉完数据后自动 `shuffle()`；随机源用 `crypto.getRandomValues` |
| **v12** | 作者行显示成「宋〕王安石」，左括号被裁 | 行首标点无前字可粘 → 退化成独立窄块（`min-width:0`），全角括号超出块宽被裁 | 行首标点缓存后**前缀给首个汉字**（见 §4.2） |
| **v11** | 长标题/作者名的拼音互相挤成一团 | v10 为求字距均匀，给标题拼音用了 `position:absolute` + `translateX(-50%)`，脱离布局宽度，长拼音贴到邻居 | 改回 **flex 列布局**，让拼音参与宽度计算。**可读性 > 字距均匀** |
| **v10** | 标题和人名没有拼音 | 只对正文做了注音 | 抽出 `buildBlocks` 复用到 title / author |
| **v9** | 隐藏拼音后行间留白很大 | 拼音节点用 `visibility:hidden` 隐藏，但它有 `height:1.15em` + `margin-top`，隐藏仍占位 | 改用 `v-if` **销毁节点**。Vue 里隐藏带固定高度的元素优先用 `v-if` |
| **v8** | 长诗（尤其宋词）排版凌乱参差 | 整句 `flex-wrap` 自动折行 | 手机端按小句强制分行 |
| **v7** | 微信内弹「加载 poems.json 失败」 | 旧 SW 在网失败时回退 `caches.match('./index.html')`，把 HTML 当 JSON 返回 | 微信内**禁用 SW**；fetch 加 `res.ok` + `content-type` 双重校验 |
| **v6** | 手机死活停在旧版，清缓存无效 | 旧 `sw.js` 把**自己**也 cache-first 了，新 SW 根本无法激活 | SW 注册加 `sw.js?v=N`；页面启动时检测旧 SW 强制 `unregister()` + reload |
| **v5** | 电脑 500 首 / 手机 70 首 | SW cache-first 缓存了旧 `poems.json`；且手机浮窗存的可能是 CloudStudio 旧链接 | 数据请求加 `?v=N` 版本戳；SW 改 network-first |
| **v4** | 注音后标点被挤压 | 标点作为独立 `char-pair` 只占窄位 | 标点粘附前字 |
| **v3** | 拼音和汉字各排各的（两层皮） | 整句汉字 + 整句拼音上下排列，未逐字绑定 | 逐字 `char-pair` flex 列对齐 |
| **v2** | 微信内排版不随屏幕缩放 | 固定 px 字号 | `clamp()` / `vw` + `100dvh` + `env(safe-area-inset-*)` |

### 由此提炼的四条通则

1. **改了 `index.html` 就必须升 `APP_VERSION`**，且 `sw.js` 的 `CACHE` 要跟着升到 `poetry-vN`。
2. **不要用 `visibility:hidden` 隐藏有高度/边距的元素**——用 `v-if` 销毁。
3. **标点粘附算法必须特判行首**——只处理"有前字"的分支会让行首标点变孤立窄块。
4. **不要为了视觉均匀而让拼音脱离布局流**（absolute 定位），长拼音必然重叠。

---

## 7. 常见修改场景 Cookbook

### 想改配色 / 字号
改 `index.html` 顶部 `:root` 的 CSS 变量（`--paper`/`--ink`/`--accent`/`--fs-*`）。改完**升版本号到 13**。

### 想加一首诗
直接编辑 `poems.json`（追加一项，`id` 顺延），然后升版本号。
> 若希望下次 `build_poems.py` 重跑时不丢，应加进 `poems_orig70.json`。

### 想改诗词排序 / 增删作者
改 `build_poems.py` 的白名单和 `PER_AUTHOR`，重跑脚本，**升版本号**。

### 想加新功能（如收藏、朗读语音）
在 `index.html` 的 Vue 实例里加 `data` / `methods` / 模板。注意：
- 需要持久化就用 `localStorage`（当前项目还没用过）。
- **不要引入 npm 依赖**，保持零构建。真需要新库就加 CDN `<script>`。

### 想彻底去掉 PWA
删 `sw.js`、删 `manifest.webmanifest`、删 `index.html` 里的 SW 注册逻辑。**升版本号**。

### 想改名字
搜索全文替换 `小诗囊`，涉及：`index.html` 的 `<title>` 和 `.brand`、`manifest.webmanifest` 的 `name`/`short_name`、`README.md`。

---

## 8. 发布与验证

### 发布
```bash
cd D:\WorkBuddy-Results\poetry-reader
git add -A
git commit -m "v13: 描述改动"
git push origin main
```
> 需要 GitHub 认证凭据。若 `git config user.name/user.email` 未设置会报错，本仓库已设为
> `hengjie1993-lang` / `hengjie1993-lang@users.noreply.github.com`。

### 验证（关键：push 后要等）

⚠️ **GitHub Pages 重建需要时间，push 完立刻 `curl` 会拿到旧版。实测约 30 秒后才更新。**

```bash
# 等 30 秒再验
curl -s "https://hengjie1993-lang.github.io/poetry-reader/index.html" | grep -oE "APP_VERSION = '[0-9]+'"
curl -s "https://hengjie1993-lang.github.io/poetry-reader/sw.js" | grep -oE "const CACHE = '[^']+'"
curl -s "https://hengjie1993-lang.github.io/poetry-reader/poems.json?v=14" | python -c "import json,sys; print('首数:', len(json.load(sys.stdin)))"
```

预期：`APP_VERSION = '14'`、`CACHE = 'poetry-v14'`、首数 500。

### 本地预览
```bash
python -m http.server 8090
# 打开 http://localhost:8090
```
> **不要 `file://` 双击打开**——`fetch` 会被浏览器拦截。

### 手机实测要点
- 用 GitHub Pages 链接，**不要**用 localhost（手机访问不到）。
- 微信里测试时 SW 是禁用的，每次都是最新代码；Safari/Chrome 走 SW，务必确认版本号升对了。

---

## 9. 环境与依赖

| 用途 | 命令 |
|---|---|
| 本地静态服务 | `python -m http.server 8090` |
| 重新编译诗词数据 | `pip install opencc-python-reimplemented` 然后 `python build_poems.py` |
| CDN 依赖 | Vue 3 + pinyin-pro，均从 jsdelivr 加载，**离线环境无法运行** |

---

## 10. 已知遗留问题 / 待办

- `PUBLISH.md` 是早期发布流程文档，现已过时（流程已稳定在 push 即发布），可考虑合并进 README 后删除。
- 备用 CloudStudio 链接 `https://94c95579db704928bac803b152eb3b8b.app.workbuddy.link` **仍停留在 v1 旧版（70 首）**，建议从 README 移除或直接下线，避免误存书签。
- 暂无收藏 / 学习进度 / 语音朗读功能（当前定位是"极简朗读"，未做）。
