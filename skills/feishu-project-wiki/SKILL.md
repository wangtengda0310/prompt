---
name: feishu-project-wiki
description: 查询、搜索、缓存飞书「卡牌项目部」知识库（Wiki 空间 7360624756670627842）里的文档。当用户提到「卡牌项目部」「项目知识库」，或说「搜索知识库」「知识库里有没有 XX 文档」「找一下 XX 的飞书文档」「查看某文档内容」「更新/刷新知识库目录」时使用。技能维护一份本地目录（2900+ 节点的层级索引）、按关键词离线搜索、并把看过的文档全文缓存到本地，飞书侧未更新时直接读缓存，避免重复拉取。支持 `--offline` 模式把文档内嵌的图片、附件、画板、表格等资源一并下载到本地，实现无网络环境下完整阅读。
compatibility:
  - Python 3.10+
  - Node.js 18+（lark-cli，需已 `lark-cli auth login`）
---

# 飞书项目知识库（卡牌项目部）

这个技能围绕一份**本地目录索引**工作：目录记录了「卡牌项目部」Wiki 空间里每个节点的标题、类型、层级路径和链接。搜索基于这份本地目录（快、离线），只有在真正查看某篇文档正文时才访问飞书，且看过一次就缓存下来。

三件事，对应三个脚本：

| 需求 | 脚本 | 说明 |
|------|------|------|
| 搜索/浏览文档 | `scripts/search_wiki.py` | 在本地目录里按关键词找文档，返回标题+层级+链接 |
| 更新目录 | `scripts/update_wiki.py` | 重新递归扫描 Wiki 空间，刷新本地目录 |
| 查看文档正文 | `scripts/fetch_doc.py` | 拉取文档全文 Markdown 并缓存；飞书未更新则读缓存；`--offline` 下载嵌入资源 |

所有脚本运行前设置 `PYTHONUTF8=1`（Windows 终端默认 GBK，否则中文乱码）。脚本内部通过 node 入口调用 lark-cli，需保证已 `lark-cli auth login`。

---

## 1. 搜索 / 浏览文档

用户想找某篇文档、或想看某个目录下有哪些内容时用。**先搜本地目录，不要直接去飞书搜。**

```bash
PYTHONUTF8=1 python scripts/search_wiki.py <关键词> [关键词2 ...] [--limit N]
```

- 多个关键词是 **AND** 语义（都要出现在标题或层级路径里），大小写不敏感。
- 命中标题的结果排在命中路径的结果前面；层级浅的优先。
- 输出每条含标题、类型标签、飞书链接和「位置」（层级路径）。

**示例**
- 用户「找卡牌项目服务器清单」→ `search_wiki.py 服务器 清单`
- 用户「策划空间下有哪些文档」→ `search_wiki.py 策划空间`（结果多时用 `--limit` 或追加关键词收窄）
- 用户「测试相关的用例文档」→ `search_wiki.py 测试 用例`

把脚本输出整理成可读列表回给用户。如果用户接着要看某篇正文，走第 3 步。

---

## 2. 更新目录

当用户明确说「更新/刷新知识库目录」，或本地目录文档 `docs/目录.md` 的顶部「导出时间」距今超过 **7 天**时，重新扫描。

```bash
PYTHONUTF8=1 python scripts/update_wiki.py
```

- 一次递归遍历整个空间（2900+ 节点，耗时约几分钟），把结果写入 `docs/目录.md`。
- 遇到瞬时 API 错误会自动重试；单节点彻底失败会记录并在结尾列出，可重跑补齐。
- 更新后向用户报告节点总数与失败数；如需对比变更，可先 `git diff docs/目录.md`。

判断是否该更新：先看 `docs/目录.md` 第 5 行左右的「导出时间：YYYY-MM-DD」。距今 >7 天且用户在做依赖目录的操作时，主动提示「目录可能已过期，要不要刷新」。

---

## 3. 查看文档正文（带缓存）

用户要读某篇文档的内容时用。**优先命中缓存，飞书侧有更新才重新拉。**

```bash
# 仅缓存 Markdown 文本（默认）
PYTHONUTF8=1 python scripts/fetch_doc.py <wiki_url_或_node_token> [--force]

# 同时下载图片/附件/画板/内嵌表格等资源，实现离线查看
PYTHONUTF8=1 python scripts/fetch_doc.py <wiki_url_或_node_token> --offline [--force]
```

- 入参可以是完整 wiki URL（`https://ztgame.feishu.cn/wiki/XXX`）或 node_token（目录/搜索结果链接里 `/wiki/` 后那段）。
- 缓存过期判断：脚本用 `wiki spaces get_node` 拿飞书侧 `obj_edit_time`，与缓存元数据比对，一致则直接读 `cache/<token>.md`，不一致则重新拉取。
- `--offline` 模式下，还会检查本地资源文件是否全部存在；任一资源缺失都会重新下载。
- `--force` 强制忽略缓存重新拉。
- 正文打到 stdout，状态信息打到 stderr。

**工作流**：从搜索结果拿到链接 → 传给 `fetch_doc.py --offline` → 把返回的 Markdown 正文整理给用户。

### 3.1 离线模式支持范围

| 嵌入类型 | 处理方式 | 本地产物 | 当前状态 |
|---|---|---|---|
| 图片（<img>） | 用飞书返回的临时 `href` 直接 HTTP 下载 | `cache/assets/<token>/image_xxx.png` | ✅ 已验证可用 |
| 视频/附件（<source>） | 同图片：优先 `href` 直接下载 | `cache/assets/<token>/attachment_xxx.mp4` | ✅ 已验证可用 |
| 画板（whiteboard） | 脚本会尝试 `whiteboard +query --output_as svg` | `cache/assets/<token>/whiteboard_xxx.svg` | ⚠️ 当前 lark-cli 版本在 Windows 下 `--output` 有 symlink 解析 bug，可能导出失败 |
| 内嵌电子表格（sheet） | `drive +export --doc-type sheet --file-extension xlsx` | `cache/assets/<token>/sheet_xxx.xlsx` | ⚠️ 需要 `docs:document.content:read` scope，当前认证可能缺失 |
| 内嵌多维表格（bitable） | `drive +export --doc-type bitable --file-extension xlsx` | `cache/assets/<token>/bitable_xxx.xlsx` | ⚠️ 同上，需要额外 scope |
| 非 docx 文档（sheet/bitable/slides/doc/file） | 整篇导出为 xlsx/pptx/pdf/原文件 | `cache/<token>.<真实扩展名>`（如 `.pptx`/`.xlsx`/`.pdf`） | ⚠️ sheet/bitable/slides 需要额外 scope；file 类型可能因飞书权限 403；mindnote 不支持 |

### 3.2 已知限制与解决方式

- **思维导图（mindnote）**：飞书 `drive +export` 不支持 mindnote，只能保留链接，无法离线保存内容。
- **file 类型下载 403**：部分云盘文件（如 PPT）因分享范围/密级限制，`drive +download` 会返回 HTTP 403。需要在飞书网页端打开该文件，确认当前账号有下载权限，或联系文件 owner 授权。
- **画板导出失败**：若看到 `cannot resolve symlinks` 错误，是当前 lark-cli（1.0.39）在 Windows 下解析 `--output` 的已知 bug。可尝试升级 lark-cli：`lark-cli update`。
- **缺少 scope（sheet/bitable/slides）**：若 `drive +export` 报 `missing required scope(s): docs:document.content:read`，运行：
  ```bash
  lark-cli auth login --scope "docs:document.content:read"
  ```
  完成授权后再试。
- **临时下载链接**：图片/附件的 `href` 只在拉取文档时短暂时效；脚本会在同一轮请求内完成下载，过期不补。
- **大视频**：首次 `--offline` 下载可能耗时较长。
- **内嵌 sheet/bitable**：导出为 Excel 后 Markdown 中只保留本地文件链接，不内联展开。

### 3.3 链接本地化（离线可跳转）

`fetch_doc.py` 拉取时会自动把文本里的飞书 wiki 文档链接 `[文字](https://ztgame.feishu.cn/wiki/<token>...)` 本地化为 `[文字](./<token>.md)`（仅当目标文档已缓存），实现离线点击跳转。block 链接（`?blockId` / `#part`）跳目标文档顶部、丢 block 锚点；未缓存目标保留原 URL。

对已缓存的大量旧文档，用 `scripts/localize_links.py` 批量后处理：

```bash
PYTHONUTF8=1 python scripts/localize_links.py                 # dry-run 统计
PYTHONUTF8=1 python scripts/localize_links.py --apply         # 实际替换
PYTHONUTF8=1 python scripts/localize_links.py --only <token>  # 单文档试跑
```

拉取新文档后目标若仍缺缓存，可 `fetch_doc.py <token> --offline` 补拉再重跑 `localize_links.py --apply`，新链接即补本地化。

---

## 4. 批量拉取子空间（batch_fetch_loop.py）

一次性把某个子空间（如「策划空间」）下所有未缓存文档拉到本地，可附带离线资源。按 `--rate` 限速分批串行拉取，适合后台跑大批量。

```bash
PYTHONUTF8=1 python scripts/batch_fetch_loop.py [选项]
```

| 选项 | 默认 | 说明 |
|------|------|------|
| `--space-node <标题>` | `策划空间` | 子空间根节点标题，在 `docs/目录.md` 缩进树中定位，拉取其全部子孙节点 |
| `--rate <N>` | `10` | 每分钟篇数上限；每批拉 N 篇，批后等到 60s 边界，保证 ≤ N 篇/分钟 |
| `--type <emoji>` | `📄文档` | 只处理该类型节点。默认只拉 docx（表格/多维表格/幻灯片缺 scope 会失败、思维导图不支持导出） |
| `--text-only` | 关 | 只缓存正文，不下载离线资源；默认下载（等价 fetch_doc 的 `--offline`） |
| `--dry-run` | 关 | 仅解析统计（节点总数 / 已缓存 / 待拉取），不拉取 |

**示例**
- 先盘点：`batch_fetch_loop.py --dry-run`
- 默认全量：`batch_fetch_loop.py`（策划空间，10 篇/分钟，含资源）
- 换子空间：`batch_fetch_loop.py --space-node 牌局战斗 --rate 5`
- 只要正文提速：`batch_fetch_loop.py --text-only --rate 20`

**行为约定**
- 已缓存判断：cache 下存在该 token 正文文件或 `.meta.json` 即跳过。
- 限速：批耗时 < 60s 则等待补足；> 60s（资源下载慢）立即开下一批，**永不超速**。离线资源下载会使实际速率低于 `--rate`，属正常。
- 失败：单篇 timeout(300s) 或失败记入失败清单，不卡死，结束统一报告，可对失败 token 单独 `fetch_doc.py <token> --offline --force` 重试。
- 进度日志：`batch_fetch_loop.log`（skill 根目录），每次运行覆盖开头；后台运行时可 `Get-Content -Tail` 查看进度。

---

## 5. 压缩离线资源（compress_assets.py）

把 cache 下所有离线图片 PNG（`assets/<token>/` 子树 + cache 根的 `whiteboard_*.png`）批量转 WebP，大幅降低磁盘占用（实测 UI 截图可省 ~92%，9 GB → 0.7 GB）。默认 dry-run 仅内存编码统计预期节省，`--apply` 实际转换并同步 `.md` / `.meta.json` 引用。

```bash
PYTHONUTF8=1 python scripts/compress_assets.py [选项]
```

| 选项 | 默认 | 说明 |
|------|------|------|
| `--apply` | 关 | 默认 dry-run 仅统计、不写盘；加 `--apply` 实际转换 |
| `--quality <N>` | `85` | WebP 质量 1-100，UI 截图 85 视觉近无损 |
| `--method <N>` | `4` | 压缩力度 0-6，越大压缩越好越慢 |
| `--only <token>` | 无 | apply 时只处理指定文档（试跑验证用） |
| `--limit <N>` | `0` | apply 时只处理前 N 个文档 |
| `--top <N>` | `10` | dry-run 显示节省最多的前 N 个文档 |

**示例**
- 预估收益：`compress_assets.py`
- 单文档试跑：`compress_assets.py --apply --only <token>`（验证引用同步正确）
- 全量执行：`compress_assets.py --apply`

**安全约定**
- 只处理 PNG（占 assets 92%）；gif/jpg/mp4 不动。
- 逐张转换，**校验 WebP 可读且非空才删原 PNG**；失败文件保留原状、引用不改。
- 引用同步用精确文件名替换（`image_XXX.png`→`image_XXX.webp`），更新 `.md` 图片路径与 `.meta.json` 的 `local_rel/local_abs/mime`。
- 建议先 `--apply --only <某文档>` 试跑、核对引用无误后再全量。
- `fetch_doc.py --force --offline` 重拉已压缩文档会恢复 PNG（offline_assets 见 png 缺失即重下），重拉后需重跑 `compress_assets.py --apply` 补齐。

---

## 6. 文件布局

```
feishu-project-wiki/
├── SKILL.md
├── docs/
│   └── 目录.md              # 维护的 Wiki 层级目录（搜索的数据源）
├── cache/
│   ├── <token>.md          # 缓存的 docx 文档正文
│   ├── <token>.pptx/xlsx/pdf # 导出的非 docx 文件
│   ├── <token>.meta.json   # 缓存元数据（obj_edit_time + assets 清单）
│   └── assets/
│       └── <token>/        # 某篇文档的离线资源（图片/画板/表格等）
└── scripts/
    ├── search_wiki.py      # 本地目录关键词搜索
    ├── update_wiki.py      # 递归重扫、刷新目录
    ├── fetch_doc.py        # 拉取正文 + 缓存（含 --offline + wiki 链接本地化）
    ├── batch_fetch_loop.py # 批量拉取子空间未缓存文档（含离线资源，限速）
    ├── compress_assets.py  # 压缩离线图片 PNG→WebP（含引用同步）
    ├── localize_links.py   # 批量本地化飞书 wiki 链接为 ./<token>.md
    └── offline_assets.py   # 离线资源下载辅助模块（含 localize_wiki_links）
```

## 7. 关键约定

- **空间 ID 固定**：`7360624756670627842`（卡牌项目部）。脚本内硬编码，本技能只服务这一个空间。
- **搜索走本地，读正文才联网**：目录索引让搜索无需每次请求飞书；只有 `fetch_doc.py` 会访问飞书，且带缓存。
- **缓存以 node_token 为键**：`cache/<token>.md` + `.meta.json`。过期依据飞书 `obj_edit_time`，不是固定 TTL。
- **离线资源以 node_token 为子目录**：`cache/assets/<token>/*`，方便整篇文档及其资源一起迁移或删除。
- **依赖 lark-cli 认证**：脚本假设 `lark-cli auth login`（user 身份）已完成，否则 `get_node` / `fetch` / `export` 会因权限失败。
