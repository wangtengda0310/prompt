---
name: ipfs-kubo
description: IPFS Kubo CLI 操作指南 - 初始化节点、添加/获取/查看/固定/删除文件、远程节点连接、仓库迁移、配置诊断。当用户提及 IPFS、Kubo、分布式存储、P2P 文件存储、CID、内容寻址、去中心化存储时触发此 skill。
tags: [ipfs, kubo, p2p, distributed, storage, cid]
---

# IPFS Kubo CLI 操作指南

本 skill 提供 IPFS Kubo CLI 的完整操作指南，包括节点管理、文件操作、固定管理、网络连接、仓库迁移和配置诊断。

## 软件安装

随 skill 发布的安装包: `./kubo_v0.40.1.zip`

### 各平台二进制文件位置
- Windows: `kubo/windows/ipfs.exe`
- Linux: `kubo/linux/ipfs`
- macOS: `kubo/darwin/ipfs`

### 安装/更新步骤
1. 停止运行的 daemon
2. 解压 `kubo_v0.40.1.zip`
3. 选择对应平台的二进制文件
4. 将 `ipfs` 可执行文件放到 PATH 目录中
5. 如需仓库迁移: `ipfs repo migrate`
6. 重启 daemon

## 核心命令速查

### 初始化与启动
```bash
ipfs init                    # 初始化仓库
ipfs daemon                  # 启动守护进程
ipfs daemon --profile server # 数据中心环境启动
ipfs id                      # 查看节点信息
ipfs version                 # 查看版本
```

### 文件操作
```bash
ipfs add <file>              # 添加文件，返回 CID
ipfs add -r <directory>      # 添加目录
ipfs get <CID>               # 下载文件到本地
ipfs get <CID> -o <path>     # 下载到指定路径
ipfs cat <CID>               # 查看文件内容（仅限文本）
ipfs ls <CID>                # 列出目录内容
ipfs refs <CID>              # 查看目录引用
```

### 固定管理
```bash
ipfs pin add <CID>           # 固定文件防止垃圾回收
ipfs pin rm <CID>            # 取消固定
ipfs pin ls                  # 列出所有固定内容
ipfs pin ls --type=recursive # 列出递归固定
ipfs repo gc                 # 执行垃圾回收
```

### 网络操作
```bash
ipfs swarm peers             # 查看连接的节点
ipfs swarm connect <peer>    # 连接指定节点
ipfs swarm disconnect <peer> # 断开节点连接
ipfs dht findpeer <peerID>   # 查找节点
ipfs ping <peerID>           # ping 节点
```

### 远程节点操作
```bash
ipfs --api /ip4/<host>/tcp/5001 <command>  # 指定远程 API
```

## 详细使用场景

### 场景1: 初始化节点

```bash
# 1. 初始化 IPFS 仓库
ipfs init

# 输出示例:
# generating ED25519 keypair...done
# peer identity: 12D3KooW...
# initializing IPFS node at ~/.ipfs

# 2. 启动守护进程（本地开发）
ipfs daemon

# 3. 数据中心/服务器环境
ipfs daemon --profile server

# 4. 验证节点运行
ipfs id
```

**注意**: `--profile server` 禁用内网穿透和 UPnP，适合公网 IP 环境。

### 场景2: 添加文件到 IPFS

```bash
# 添加单个文件
ipfs add myfile.txt
# 输出: QmXyz... myfile.txt

# 添加目录
ipfs add -r myfolder/

# 添加时固定（默认行为）
ipfs add --pin myfile.txt

# 只添加不固定
ipfs add --pin=false myfile.txt

# 使用 CIDv1（推荐）
ipfs add --cid-version=1 myfile.txt
```

**返回的 CID** 是文件的内容标识符，可用于全球访问。

### 场景3: 从 IPFS 获取文件

```bash
# 下载文件到当前目录
ipfs get QmXyz...

# 下载到指定路径
ipfs get QmXyz... -o ./downloaded.txt

# 下载目录
ipfs get QmDirCID... -o ./myfolder
```

### 场景4: 查看文件内容

```bash
# 查看文本文件内容
ipfs cat QmXyz...

# 输出到文件
ipfs cat QmXyz... > output.txt

# 查看目录结构
ipfs ls QmDirCID...
```

**注意**: `ipfs cat` 仅适用于文本文件，二进制文件会显示乱码。

### 场景5: 固定与删除文件

```bash
# 固定文件（防止垃圾回收）
ipfs pin add QmXyz...

# 取消固定
ipfs pin rm QmXyz...

# 查看固定状态
ipfs pin ls
ipfs pin ls QmXyz...

# 执行垃圾回收（删除未固定内容）
ipfs repo gc
```

**工作原理**:
- `ipfs add` 默认固定文件
- 只有取消固定后，垃圾回收才会删除文件
- 固定确保文件在本地持久存储

### 场景6: 连接远程节点

```bash
# 方式1: 使用 --api 标志
ipfs --api /ip4/192.168.1.100/tcp/5001 add myfile.txt
ipfs --api /ip4/192.168.1.100/tcp/5001 cat QmXyz...

# 方式2: 设置 API 文件
echo "/ip4/192.168.1.100/tcp/5001" > $IPFS_PATH/api
ipfs cat QmXyz...  # 自动使用远程 API
```

**安全警告**:
- RPC API (5001 端口) 不应暴露到公网
- 远程连接应使用 TLS 和认证
- 默认 API 只监听 localhost

## 仓库和配置迁移

### 仓库位置
- Linux/macOS: `~/.ipfs`
- Windows: `%USERPROFILE%\.ipfs`
- 可通过 `IPFS_PATH` 环境变量修改

### 迁移步骤

```bash
# 1. 停止 daemon
# 找到并终止 ipfs daemon 进程

# 2. 备份仓库
cp -r ~/.ipfs ~/.ipfs.backup

# 3. 迁移到新位置
mv ~/.ipfs /new/location/.ipfs

# 4. 设置环境变量
export IPFS_PATH=/new/location/.ipfs

# 5. 重启 daemon
ipfs daemon
```

### 跨机器迁移

跨机器迁移需要注意:
1. **Peer Identity**: 每个节点有唯一的 PeerID 和私钥
2. **网络配置**: Swarm 地址需要适配新机器
3. **数据完整性**: 确保复制完整

```bash
# 在新机器上
# 方式1: 复制整个仓库
scp -r old-machine:~/.ipfs ~/.ipfs

# 方式2: 只复制 identity (新节点)
# 初始化新节点，然后只复制 config 中的 Identity 部分
```

## 配置文件解读

### 配置文件位置
`$IPFS_PATH/config` (JSON 格式)

### 关键配置项

```json
{
  "Identity": {
    "PeerID": "12D3KooW...",     // 节点唯一标识
    "PrivKey": "CAES..."         // 私钥（敏感！）
  },
  "Addresses": {
    "Swarm": [                   // P2P 监听地址
      "/ip4/0.0.0.0/tcp/4001",
      "/ip6/::/tcp/4001"
    ],
    "API": "/ip4/127.0.0.1/tcp/5001",     // RPC API
    "Gateway": "/ip4/127.0.0.1/tcp/8080"  // HTTP 网关
  },
  "Mounts": {
    "IPFS": "/ipfs",             // FUSE 挂载点
    "IPNS": "/ipns"
  },
  "Datastore": { ... },          // 数据存储配置
  "Bootstrap": [ ... ],          // 引导节点列表
  "Gateway": {
    "RootRedirect": ""           // 网关根路径重定向
  }
}
```

### 常用配置命令

```bash
# 显示当前配置
ipfs config show

# 获取特定配置项
ipfs config Addresses.API
ipfs config Identity.PeerID

# 设置配置项
ipfs config Addresses.Gateway "/ip4/0.0.0.0/tcp/8080"

# 设置 JSON 配置
ipfs config --json Addresses.Swarm '["/ip4/0.0.0.0/tcp/4001"]'

# 添加 Bootstrap 节点
ipfs bootstrap add <peer-multiaddr>
```

### 配置诊断

```bash
# 检查端口占用
netstat -tlnp | grep -E '4001|5001|8080'

# 验证引导节点连接
ipfs bootstrap list

# 测试网络连接
ipfs swarm peers
ipfs ping <peerID>

# 检查仓库状态
ipfs repo stat
ipfs repo verify
```

### 常见配置问题

1. **端口冲突**: 修改 `Addresses.Swarm`、`Addresses.API`、`Addresses.Gateway`
2. **无法连接节点**: 检查防火墙和 Bootstrap 配置
3. **存储空间**: 查看 `ipfs repo stat` 了解使用情况
4. **网关访问**: 确认 Gateway 地址绑定到 `0.0.0.0` 允许外部访问

## 安全注意事项

1. **API 端口 (5001)**: 默认只监听 localhost，不要暴露到公网
2. **Gateway 端口 (8080)**: 可配置公开访问，但有速率限制
3. **私钥保护**: `Identity.PrivKey` 是敏感信息，不要泄露
4. **远程连接**: 使用 TLS 和认证机制

## 常见问题

### Q: 如何查看节点是否正常运行?
```bash
ipfs id                    # 查看节点信息
ipfs swarm peers           # 查看连接的节点
```

### Q: 文件添加后其他节点无法访问?
- 确认 daemon 正在运行
- 检查防火墙是否开放 4001 端口
- 确认文件已固定

### Q: 如何完全删除一个文件?
```bash
ipfs pin rm <CID>          # 取消固定
ipfs repo gc               # 垃圾回收
```

### Q: 如何在后台运行 daemon?
```bash
# Linux/macOS
nohup ipfs daemon > ipfs.log 2>&1 &

# 或使用 systemd/supervisor 等进程管理器
```

### Q: 仓库太大怎么办?
```bash
ipfs repo stat             # 查看仓库统计
ipfs repo gc               # 垃圾回收
ipfs pin ls                # 检查固定内容
```
