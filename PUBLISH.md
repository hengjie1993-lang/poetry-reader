# 发布到手机可用 · GitHub Pages 三步

> 现状：`localhost:8099` 只在本机（电脑）能用，手机访问不到。
> 目标：拿到一个公网链接 `https://<你的用户名>.github.io/poetry-reader/`，
> 微信里打开 → 点「···」→ 浮窗；或浏览器「添加到主屏幕」，以后秒开。

---

## ✅ 我已经帮你做好的

项目已 `git init` 并提交了初版（commit `140837e`），包含：

```
README.md  index.html  manifest.webmanifest  poems.json  sw.js
```

你只需补「推到 GitHub」和「开 Pages」两步即可。

---

## 第 1 步：GitHub 网页新建空仓库

1. 打开 https://github.com/new
2. Repository name 填：`poetry-reader`
3. **不要**勾选 "Add a README file"（否则首次 push 会冲突）
4. 点 Create repository

## 第 2 步：推送到 GitHub

在 `D:\WorkBuddy-Results\poetry-reader` 目录打开终端（Git Bash / PowerShell），把下面三行里的
`<你的用户名>` 换成你真实的 GitHub 用户名，粘贴执行：

```bash
git remote add origin https://github.com/<你的用户名>/poetry-reader.git
git branch -M main
git push -u origin main
```

> 推送时会要求登录 GitHub。密码栏请填 **Personal Access Token**（GitHub 已不支持账号密码 push），
> Token 在 https://github.com/settings/tokens 生成，勾 `repo` 权限即可。

## 第 3 步：开启 GitHub Pages

1. 进入仓库 → **Settings** → 左侧 **Pages**
2. Source 选 **Deploy from a branch**
3. Branch 选 **main** / 目录 **/ (root)** → Save
4. 等 1~2 分钟，访问：`https://<你的用户名>.github.io/poetry-reader/`

---

## 在手机上使用

- **微信浮窗（最顺手）**：把上面的链接发到「文件传输助手」→ 在微信里打开 → 点右上角「···」→ 浮窗。
  之后从微信浮窗列表点开即秒开，且首次联网后离线也能看（PWA 缓存）。
- **浏览器书签**：Safari/Chrome 打开链接 → 分享 → 添加到主屏幕 / 加书签。
- **搜索**：顶栏输入标题、作者、朝代、任意诗句或拼音（如「李白」「春」「宋」「chun」）即时过滤。

---

## 临时方案：同一 WiFi 下免发布（不推荐长期使用）

适合你**现在**就想在手机上试：

1. 电脑保持 `python -m http.server 8099` 运行（当前已在后台运行）
2. 电脑 `cmd` 里敲 `ipconfig`，找到「无线局域网适配器 WLAN」下的 **IPv4 地址**（形如 `192.168.x.x`）
3. 手机连**同一个 WiFi**，浏览器访问 `http://<那个IPv4>:8099`

缺点：手机重启/IP 变了就失效、出门用不了、微信浮窗可能拉不起。仅临时尝鲜用。

---

## 之后怎么更新内容

- 增删诗词：直接编辑 `poems.json`（每条含 `id/title/author/dynasty/paragraphs`），
  保存后重新 `git add -A && git commit -m "更新" && git push` 即可。
- 想扩到 300+ 首：让我跑批量导入脚本从开源 MIT 库灌入。
