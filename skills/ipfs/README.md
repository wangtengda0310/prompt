# IPFS Kubo CLI Skill

Claude Code 使用的 IPFS Kubo CLI 操作技能。

## 包含的软件

- `kubo_v0.40.1.zip`: Kubo v0.40.1 安装包（包含 Windows/Linux/macOS 二进制文件）

## 安装

### 方法1: 复制到 Claude Code skills 目录

```bash
# 将此目录复制到你的 skills 目录
cp -r ./ipfs ~/.claude/skills/
```

### 方法2: 使用 skill 文件安装

如果有 `.skill` 文件，直接双击或通过 Claude Code 安装。

## 前置要求

- 安装 Kubo CLI (`ipfs` 命令)
- 可使用随 skill 发布的 `kubo_v0.40.1.zip` 进行安装

### 从安装包安装

```bash
# 1. 解压安装包
unzip kubo_v0.40.1.zip

# 2. 选择对应平台的二进制文件
# Windows: kubo/windows/ipfs.exe
# Linux: kubo/linux/ipfs
# macOS: kubo/darwin/ipfs

# 3. 放到 PATH 目录
# Linux/macOS
sudo cp kubo/linux/ipfs /usr/local/bin/

# Windows
# 将 ipfs.exe 复制到 PATH 目录，如 C:\Windows\
```

## 使用方法

在 Claude Code 中提及 IPFS 相关操作即可触发此 skill。

### 触发关键词

- IPFS、Kubo
- 分布式存储、P2P 存储
- CID、内容寻址
- 去中心化存储

### 示例请求

```
"帮我初始化一个 IPFS 节点"
"把这个文件添加到 IPFS"
"从 IPFS 获取 QmXyz... 这个文件"
"固定这个 CID"
"查看我的 IPFS 配置"
"把 IPFS 仓库迁移到新位置"
```

## 支持的操作

| 操作类型 | 支持的命令 |
|---------|-----------|
| 节点管理 | init, daemon, id, version |
| 文件操作 | add, get, cat, ls, refs |
| 固定管理 | pin add, pin rm, pin ls, repo gc |
| 网络操作 | swarm peers, swarm connect |
| 远程操作 | --api 远程节点操作 |
| 配置管理 | config show, config get/set |
| 仓库管理 | repo stat, repo verify, 迁移 |
| 软件更新 | 使用 kubo_v0.40.1.zip |

## 软件更新

### 使用随 skill 发布的安装包

1. 停止 daemon
2. 解压 `kubo_v0.40.1.zip`
3. 选择对应平台的二进制文件替换旧版本
4. 重启 daemon

### 仓库迁移

更新后可能需要运行:

```bash
ipfs repo migrate
```

## 仓库迁移指南

### 默认仓库位置

| 平台 | 路径 |
|-----|------|
| Linux/macOS | `~/.ipfs` |
| Windows | `%USERPROFILE%\.ipfs` |

### 迁移步骤

```bash
# 1. 停止 daemon
pkill ipfs  # Linux/macOS

# 2. 备份仓库
cp -r ~/.ipfs ~/.ipfs.backup

# 3. 移动到新位置
mv ~/.ipfs /new/path/.ipfs

# 4. 设置环境变量
export IPFS_PATH=/new/path/.ipfs

# 5. 重启 daemon
ipfs daemon
```

## 常用命令速查

```bash
# 初始化
ipfs init

# 启动
ipfs daemon

# 添加文件
ipfs add myfile.txt

# 获取文件
ipfs get QmXyz...

# 查看文件
ipfs cat QmXyz...

# 固定文件
ipfs pin add QmXyz...

# 删除文件
ipfs pin rm QmXyz...
ipfs repo gc

# 查看配置
ipfs config show

# 连接节点
ipfs swarm peers
```

## 安全提示

- RPC API (5001) 默认只监听 localhost，不要暴露到公网
- 远程连接应使用 TLS 和认证
- 保护 `~/.ipfs/config` 中的私钥

## 更多资源

- [IPFS 官方文档](https://docs.ipfs.tech/)
- [Kubo 安装指南](https://docs.ipfs.tech/install/command-line/)
- [Kubo 基础 CLI](https://docs.ipfs.tech/how-to/kubo-basic-cli/)
- [命令行快速入门](https://docs.ipfs.tech/how-to/command-line-quick-start/)
