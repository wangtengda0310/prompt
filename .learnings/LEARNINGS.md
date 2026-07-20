# 经验教训（LEARNINGS）

## 2026-07-20 · API key 误提交公开仓库被 GitHub Push Protection 拦截

**现象**：`git push` 被远程拒绝，报错 `GH013: Repository rule violations found`，定位到 `skills/各种apikey/SKILL.md:37` 的飞书 App Secret。

**根因**：
- `skills/各种apikey/SKILL.md` 这个 skill 文件被当作"个人密钥备忘录"直接 track 进 git，里面写了 5 个真实密钥（DeepSeek、Kling AK/SK、飞书 appId+secret、skillhub token）。
- 其中 DeepSeek/Kling 3 个密钥在更早的提交 `9e33adc` 就已经推送到**公开**仓库 origin/master，GitHub 当时没拦（这几种格式不在它的扫描模式里）；这次新增的飞书 secret 命中 Lark 扫描模式才被拦下。
- 教训：**密钥备忘类文件一开始就不该进 git**。GitHub Push Protection 只覆盖它认识的密钥格式，不代表没被拦就是安全的。

**处理**：用 `git-filter-repo --replace-text` 把 6 个 secret 字符串替换为 `REDACTED_*` 占位符，改写全部历史后 `git push --force-with-lease` 强推覆盖远程。全历史 grep 验证 0 残留。

**预防（How to apply）**：
1. 真实密钥只放在 `.env` / 密码管理器 / 本地不 track 的文件里；仓库里只留占位符模板。
2. 个人"密钥备忘录"如需保留，加进 `.gitignore`，或在文件名上区分（如 `*.local.md`）并配套 ignore 规则。
3. 提交前对包含 `api_key`/`secret`/`token` 的改动保持警觉：`git diff --cached` 扫一眼再 commit。
4. **密钥一旦进过公开仓库（哪怕后来改写历史）一律视为泄露**，必须到各平台轮换。改写历史无法清除已发生的泄露：GitHub 缓存、fork、clone、爬虫、密钥扫描告警都可能在改写前已经拿到。

**工具备忘**：
- `git-filter-repo` 通过 `py -m pip install git-filter-repo -i https://pypi.tuna.tsinghua.edu.cn/simple` 安装，`.exe` 落在 `~/AppData/Roaming/Python/Python314/Scripts/`（不在 PATH，需全路径调用）。
- filter-repo 默认会移除 origin 远程并要求 `--force`（非 fresh clone）；改写后需 `git remote add origin <url>` 重新加回。
- 改写前务必 `git bundle create xxx.bundle --all` 做全量备份；替换规则文件含明文密钥，放在仓库外并在用完后删除。
