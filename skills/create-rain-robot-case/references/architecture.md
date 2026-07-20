# rain-robot 架构参考

本文件提供 rain-robot 框架的补充架构细节。SKILL.md 已包含核心内容，这里提供更深入的技术参考。

## 目录

1. [TCP 消息编码细节](#tcp-消息编码细节)
2. [ByteStream 序列化详解](#bytestream-序列化详解)
3. [HTTP 登录协议细节](#http-登录协议细节)
4. [LoginModule 完整流程](#loginmodule-完整流程)
5. [消息注册机制详解](#消息注册机制详解)
6. [SyncMap 完整映射表](#syncmap-完整映射表)
7. [多机器人协作模式](#多机器人协作模式)
8. [参考用例列表](#参考用例列表)

## TCP 消息编码细节

### 发送流程（SendTcpMsg）

```
1. seqID + 1
2. EncodeMsg:
   a. GetSizeNew(msg) — 计算消息 ByteStream 编码后的总大小
   b. 分配 buffer: [4B占位][2B MsgID][4B SeqID][payload...]
   c. SerializeNewWithBuff — 将 msg 用 ByteStream 序列化到 payload 部分
      - 自定义消息：按字段顺序直接写入二进制
      - Proto 消息：先 proto.Marshal → 再 WriteBytes([2B长度][proto数据])
3. CompressAndEncrypt: 对 buf[4:] 整体做 snappy压缩(>100字节) + XOR加密
4. setMsgBufLen: 前3字节填入 buf[4:] 的总长度
5. conn.Write: 发送完整帧
```

### 接收流程（ListenTcpMsg）

```
1. 读取 4 字节 Header [长度3B][标志位1B]
2. 根据 Header 中的长度读取消息体
3. 根据标志位决定是否解密、解压（与发送流程对称）
4. 解析 [MsgID(2B)][SeqID(4B)][payload]
5. 根据 MsgID 查注册表，用 ByteStream 反序列化 payload 为具体类型
   - 自定义消息（<1000）：按字段顺序从 ByteStream 读取
   - Proto 消息（>=1000）：先 ReadBytes 去掉 [2B长度] 头 → 再 proto.Unmarshal
6. 放入 RecvMsgBuf 供 Wait() 消费
```

### 加密算法

XOR 加密，实现在 `xcard_net_lib/encrypt.go`。

密钥定义在 `xcard_net_lib/key.go`：
- `encryptKey = []byte{253, 1, 56, 52, 62, 176, 42, 138}` — 服务端加密用
- `decryptKey = []byte{41, 247, 6, 255, 138, 78, 197, 129}` — 客户端加密用

加密流程（`EncryptData`）：
```
for each byte buf[i]:
    n = (i % 7) + 1                    // 移位长度 1-7
    b = (buf[i] << n) | (buf[i] >> (8 - n))  // 循环左移 n 位
    buf[i] = b ^ key[i % keylen]       // XOR 密钥
```

**关键**：客户端加密使用 `decryptKey`（不是 `encryptKey`），客户端解密使用 `encryptKey`。这是设计上的密钥对调。

### 压缩算法

snappy 压缩，仅当消息体 > 100 字节时启用。

## ByteStream 序列化详解

ByteStream 是 rain-robot 框架的统一序列化层，实现在 `xcard_msg_def/serialize.go`。**所有消息（包括 proto 消息和自定义消息）都经过 ByteStream 序列化后才放入 TCP 帧的 payload 部分。**

### 序列化流程

```
EncodeMsg(msg, msgID, seqID)
  ↓
1. 分配 buffer: [MsgHeadSize=4][MsgID=2B][SeqID=4B][GetSizeNew(msg) 字节]
2. 写入 MsgID 和 SeqID
3. SerializeNewWithBuff(buf[10:], msg)  ← ByteStream 序列化 payload
```

### ByteStream 类型映射

| Go 类型 | ByteStream 格式 | 说明 |
|---------|-----------------|------|
| `bool` | `[1B]` | 0=false, 1=true |
| `int8/uint8` | `[1B]` | |
| `int16/uint16` | `[2B LE]` | |
| `int32/uint32/float32` | `[4B LE]` | |
| `int64/uint64/float64` | `[8B LE]` | |
| `string` | `[2B长度LE][N字节内容]` | |
| `[]byte` | `[2B长度LE][N字节数据]` | |
| `map[K]V` | `[2B长度][key1][val1][key2][val2]...` | |
| `[]T` (非[]byte) | `[2B长度][elem1][elem2]...` | |
| `struct` | 按字段顺序依次序列化 | 递归处理每个字段 |
| `*ProtoMsg` (proto指针) | `[2B长度LE][proto Marshal 数据]` | **先 proto.Marshal，再 WriteBytes 包装** |

### Proto 消息的 ByteStream 包装（最容易踩的坑）

当消息是 proto 结构体指针时，ByteStream 的 `serialize()` 函数（`serialize.go:176`）走特殊路径：

```go
case reflect.Ptr:
    if protoMsg, ok := val.Interface().(IProtoMsg); ok {
        tmpData := make([]byte, protoMsg.Size())
        protoMsg.MarshalTo(tmpData)     // 1. 先做 proto Marshal
        bw.WriteBytes(tmpData)          // 2. 再用 [2B长度][数据] 包装
    }
```

**这意味着 TCP 帧中的 proto payload 格式是：**
```
[2字节长度LE][protobuf Marshal 二进制数据]
```

**不是裸 protobuf！** 这一点在独立实现通信时（不使用 rain-robot 框架）至关重要。

#### 反序列化同理

接收端在 `unserialize()` 中（`serialize.go:268`）：
```go
case reflect.Ptr:
    if protoMsg, ok := val.Interface().(IProtoMsg); ok {
        buff, _ := bw.ReadBytes()       // 1. 先读 [2B长度][数据]
        protoMsg.Unmarshal(buff)         // 2. 再 proto Unmarshal
    }
```

### 自定义消息序列化示例

LoginReq（MsgID=1）的字段和 ByteStream 编码：

```
字段: Account(string), Token(string), UID(uint64), Version(string),
      Metadata(map[string]uint64), ExtData([]byte), ReqType(uint16),
      SeqID(uint32), Entity(string), Sign(string)

编码: [2B:Account长度][Account内容][2B:Token长度][Token内容][8B:UID=0]
      [2B:Version长度][Version内容][2B:map长度=0][2B:bytes长度=0]
      [2B:ReqType=0][4B:SeqID=0][2B:Entity长度=0][2B:Sign长度=0]
```

## HTTP 登录协议细节

### 请求

```
POST http://{ServerIp}:{ServerPort}/authlogin
Content-Type: application/json

{
    "accessToken": "123",
    "uid": "botPrefix_botIdx",
    "sdk": "FakeSDK",
    "platform": "Android"
}
```

### 响应

```json
{
    "code": 0,
    "token": "eyJhbGci...",
    "serverAddr": "10.254.114.204:18000"
}
```

- `code=0` 成功，`code=-700` 服务器满（会自动重试）
- `serverAddr` 是 TCP 地址，端口由服务端动态分配（不同于 HTTP 端口 20144）

### 相关结构体

- `HttpLoginAuthReq` — `xcard_tcp/http_login.go:20`
- `HttpLoginRespToClient` — `xcard_tcp/http_login.go:46`

## LoginModule 完整流程

```
1. 随机化登录时间（1-3秒延迟，避免同时登录）
2. HTTP 认证 → 获取 Token + ServerAddr
3. TCP 连接 ServerAddr
4. 启动 ListenTcpMsg 协程（接收消息循环）
5. 启动心跳协程（每5秒 Ping）
6. 发送 LoginReq {Account, Token, UID, Version}
7. 等待 LoginResp
8. 等待 RefreshUserDataNtf（PlayerInfo, IsHaveRole）
9. 如果 IsHaveRole=false:
   a. 生成角色名
   b. 发送 CreateRoleReq
   c. 等待 CreateRoleAck
10. 等待 LoginServerMsgOverNtf（初始推送结束标记）
11. 返回
```

## 消息注册机制详解

### 两级注册

1. **类型注册**（`message.go` 的 `RegisterMsg`）：
   将 MsgID → Go 类型映射，用于反序列化

```go
p.RegMsg(xcard_msg_def.MsgID(EGameMsgID_StartMatchReq_id), new(StartMatchReq))
```

2. **用例注册**（`cases.go` 的 `RegisterCases`）：
   将用例名 → Go 类型映射，用于创建用例实例

```go
p.RegCase("MatchCase", MatchCase{})
```

### 自定义消息的处理

MsgID < 1000 的自定义消息（LoginReq, Ping 等）在 `ListenTcpMsg` 中硬编码处理，不经过注册表。它们的结构体定义在 `xcard_msg_def/client_msg.go`。

## SyncMap 完整映射表

| SyncMap Key | 数据类型 | 来源消息 | 说明 |
|-------------|----------|----------|------|
| `PlayerInfo` | `*protoMsg.PlayerInfo` | RefreshUserDataNtf | 玩家基础信息 |
| `IsHaveRole` | `bool` | RefreshUserDataNtf | 是否已创建角色 |
| `ItemList` | `*protoMsg.UserItemListNtf` | UserItemListNtf | 物品列表 |
| `HeroItemList` | `[]*protoMsg.HeroInfo` | UserHeroListNtf / UpdateUserHeroNtf | 武将列表 |
| `RoomInfo` | `*protoMsg.RoomInfo` | RoomNtf / ReconnectRoomNtf | 房间信息 |
| `StartBattleNtf` | `*protoMsg.StartBattleNtf` | StartBattleNtf | 战斗开始信息 |
| `PlayerIdHeroIdMap` | `map[uint64]uint32` | StartBattleNtf | 玩家ID→武将ID映射 |
| `Circle` | 牌堆信息 | CardPileNtf / StartBattleNtf | 当前牌堆 |
| `BattleProperty` | 战斗属性 | UpdatePropertyNtf | 战斗中属性 |
| `RoomGameActionNtf` | `*protoMsg.RoomGameActionNtf` | RoomGameActionNtf | 房间游戏动作 |
| `ActivityInfo` | `map[uint32]*protoMsg.ActSaveInfo` | UserActivityInfoNtf | 活动数据 |
| `Season` | 赛季号 | SeasonInfoUpateNtf | 当前赛季 |
| `SeasonPassData` | 战令数据 | SeasonPassInfoNtf | 战令信息 |
| `PartnerList` | 伙伴列表 | UserPartnerListNtf | 伙伴信息 |
| `GuildId` | `uint64` | GuildUserLoginNtf | 工会ID |
| `PveRougeStageInfoNtf` | `*protoMsg.PveRougeStageInfoNtf` | PveRougeStageInfoNtf | 肉鸽关卡信息 |
| `PveRougeStageMapInfoNtf` | `*protoMsg.PveRougeStageMapInfoNtf` | PveRougeStageMapInfoNtf | 肉鸽地图信息 |

### 读取示例

```go
// 玩家ID
playerInfo := c.SyncMapGet("PlayerInfo").(*protoMsg.PlayerInfo)
playerID := playerInfo.SimpleInfo.PlayerID

// 武将数量
heroes := c.SyncMapGet("HeroItemList").([]*protoMsg.HeroInfo)
count := len(heroes)

// 工具函数
playerID := GetPlayerID(c)  // robot_utils.go:11
```

## 多机器人协作模式

### 多机器人索引计算

```go
botNumInProcess := envSnapshot.GetEnvInt("CASE_BOT_NUM", vars.BotNum)
idxOffset := envSnapshot.GetEnvInt("CASE_IDX_OFFSET", 0)
_, _, idx := c.GetName()  // idx 是当前机器人在进程内的编号(0-based)

// 找到后面的第 i 个机器人编号
nextIdx := GetNextNBotIndexInCaseCycle(idx, i, botNumInProcess, idxOffset)
```

### 多机器人命名规则

机器人全名格式：`{PREFIX}_{idxOffset + idx + 1}`，idx 从 0 开始。

例如 PREFIX=test, BOT_NUM=5, IDX_OFFSET=0 → 机器人名为 test_1, test_2, ..., test_5。

### 多进程部署

设置 `PROCESS_NUM` 启动多个进程，每个进程负责一段连续的机器人编号。通过 `CASE_IDX_OFFSET` 错开。

## 参考用例列表

现有 30 个用例，按功能分组：

### 登录模块
- `LoginCase` — 基础登录
- `LoginPhoneVerifyCase` — 手机验证码登录
- `LogoutCycleCase` — 循环登出登录
- `GenOldAccountCase` — 生成老账号数据

### 战斗模块
- `RoomBotAIChatCase` — 房间 AI 聊天
- `PveBossCase` — PVE Boss 战
- `PveRougeCase` — 肉鸽模式
- `PveRougeLazyGenerateCase` — 肉鸽懒加载
- `MatchCase` — 匹配系统
- `LookCase` — 观战
- `GuildWarCase` — 工会战
- `Fight8FunctionCase` — 8人战斗功能测试

### 好友模块
- `FriendListCase` — 好友列表
- `FriendSearchCase` — 搜索好友
- `FriendApplyCase` — 申请好友
- `FriendChatCase` — 好友聊天
- `FriendGiftCase` — 好友送礼
- `FriendAgreeCase` — 同意好友

### 其他
- `MailCase` — 邮件系统
- `RankListCase` — 排行榜
- `SpecialListCase` — 特殊排行榜
- `CollectCase` — 收藏系统
- `GuildCase` — 工会系统
- `ActivityCase` — 活动系统
- `RechargeCase` — 充值系统
- `DrawCase` — 抽卡
- `RedisCase` — Redis 锁测试
- `ProtoCase` — Proto 协议测试
- `YanwuQAFunctionCase` — 演武 QA 功能自动化
- `TestCase` — 基础测试
