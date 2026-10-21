# Hao Hu 个人学术主页：修改与预览

这是基于你指定的 [qizhang94/qizhang94.github.io](https://github.com/qizhang94/qizhang94.github.io) 模板制作的静态 HTML 版本，沿用 Minimal Light 双栏布局。无需安装 Ruby、Jekyll 或额外 Python 包。

## 现在怎样查看

双击 `dist/index.html` 即可用浏览器查看。这个文件可以直接离线打开，论文筛选和搜索也可用。

当前没有启用 GitHub Pages，也没有公开部署。`noindex` 和 `robots.txt` 只是搜索引擎提示，不是访问控制；草稿的私密性来自仅保存在本地、以及如已上传时使用私人仓库。

## 怎样修改

1. 用 VS Code 或记事本打开 `content.json`，修改英文正文，保存为 UTF-8。
2. 双击 `修改后生成网页.cmd`。窗口显示 `Built dist/index.html` 就表示生成成功，会自动打开主页。
3. 刷新原来的浏览器标签查看修改。

若电脑没有正确配置 `python`，在此文件夹终端执行：

```powershell
& 'G:\JupyterNotebook\python.exe' .\scripts\build.py
```

网页由 `content.json` 自动生成。不要直接编辑 `dist/index.html`，下一次生成会覆盖该文件。

| 要改的内容 | content.json 中的位置 |
| --- | --- |
| 姓名、身份、邮箱、学校、个人链接 | `profile` |
| About me 正文 | `about`，每个引号内是一段 |
| 研究方向 | `interests` |
| 新闻 | `news`，最新的放最前面；`url` 可留空 |
| 教育背景 | `education` |
| 工作与研究经历 | `experience` |
| 论文 | `publications` |
| 评估报告 | `reports` |
| 审稿、教学与导师工作 | `services` |
| 荣誉与奖项 | `awards` |

JSON 的引号、逗号、方括号需要保留。句中需要英文双引号时写成 `\"`。同一数组内两条记录之间需要逗号，最后一条记录后面不要加逗号。

### 添加论文

在 `publications` 数组里复制一条记录，修改为：

```json
{
  "title": "Your paper title.",
  "authors": "Hao Hu, Other Author",
  "venue": "Journal name, volume, pages (year).",
  "status": "Published",
  "group": "published",
  "url": "https://doi.org/your-doi",
  "visible": true
}
```

`group` 只使用以下三个值，它控制论文分组和筛选：

- `published`：已发表或已接收。接收但未发表时，`status` 使用 `Accepted`。
- `review`：预印本、审稿中或已投稿。请在 `status` 和 `venue` 写明真实状态。
- `preparation`：准备中的论文。

`visible` 改为 `false` 可以暂时隐藏某篇论文。`url` 没有时保留空字符串 `""`。作者行中的 `Hao Hu` 会自动加粗，`#` 表示共同第一作者。论文状态沿用本次提供的 CV，之后需要由你更新。

### 更换头像

用新照片替换 `assets/img/portrait.png`，再生成网页。也可以在 `profile.portrait` 改成新文件的相对路径。当前照片来自你提供的 LinkedIn 页面。

### 修改样式

修改 `assets/css/custom.css`，顶部 `:root` 内可调整主题色。不要优先改 `minimal-light.css`，它是保留的模板样式。

## 发布前要看什么

先读 `CONTENT_REVIEW.md`，核对任职日期和奖项年份。原始 CV 没有放入网站，住址、电话也没有放入网页；学校邮箱已保留。

你确认后，可以让 Codex 将这份草稿发布到你的 GitHub Pages。预计地址为 `https://haohuresearch.github.io/`，以实际仓库和 Pages 设置为准。发布时需要：

1. 确认你愿意公开的论文、审稿状态和个人经历；按需隐藏准备中的文章。
2. 将 `dist` 作为站点内容部署；仅将仓库改成 Public 并不等于网页已发布。
3. 移除构建脚本中的 `noindex, nofollow` 与 `robots.txt` 的全站禁止规则，再重新生成。
4. 配置正式网址、检查链接和手机布局，然后启用 Pages。

这份草稿没有自动发布的工作流。修改或上传源文件不会自行启用 Pages。

## 文件结构

```text
content.json              # 以后主要修改这个文件
assets/                   # 源样式、头像、脚本
scripts/build.py          # 生成网页，Python 标准库即可
scripts/serve.py          # 可选的本地预览服务器，仅监听 127.0.0.1
修改后生成网页.cmd          # 双击生成并打开
dist/                     # 实际网页，未来只部署这个目录
CONTENT_REVIEW.md         # 本次内容来源和待确认事项
TEMPLATE_SOURCE.md        # 模板来源、版本与改动
LICENSE                   # 上游模板 CC0 许可
```
