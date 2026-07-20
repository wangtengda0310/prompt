---
name: create-rain-robot-case
description: 指导 AI 从零开发 rain-robot 机器人测试脚本。覆盖 proto 协议知识、TCP 通信细节、登录流程、Call/Wait 模式、GM 命令、属性同步、用例注册全流程。当用户要求"写一个新的测试用例"、"新增机器人脚本"、"开发 proto 测试"、"测试某个功能"、"新建 Case"、"添加测试场景"、"帮我测试 XXX 功能"时必须使用此 skill。也适用于开发不依赖 rain-robot 框架的独立工具（如 GM 工具、调试工具）。即使 AI 对 rain-robot 完全陌生，仅凭此 skill 也应能开发出可运行的测试脚本或独立程序。
---

# 从零开发 rain-robot 测试脚本

本 skill 是一个完整的开发指南，让不了解 rain-robot 的 AI 也能开发出可运行的测试脚本。

## 第一步：理解整体架构

rain-robot 是一个 Go 语言游戏服务器压测/QA 测试框架。机器人通过 **HTTP 认证 + TCP 通信** 与游戏服务器交互，使用 protobuf 协议收发消息。

```
┌─────────┐   HTTP POST /authlogin    ┌──────────┐
│  机器人  │ ─────────────────────────→ │ 登录服务  │
│         │ ← Token + ServerAddr      │          │
│         │                            └──────────┘
│         │   TCP Connect (ServerAddr)  ┌──────────┐
│         │ ─────────────────────────→ │ 游戏服务  │
│         │ ←→ protobuf 消息双向通信    │          │
└─────────┘                            └──────────┘
```

### 关键目录结构

```
rain-robot/
├── robot/robot_i.go              # Robot 接口（Call/Wait/SyncMap）
├── project/xcard/
│   ├── xcard_pb/                 # proto 生成的 Go 代码
│   │   ├── msgId.pb.go           # 消息 ID 枚举 EGameMsgID
│   │   ├── lobby.pb.go           # 业务协议结构体
│   │   ├── room.pb.go            # 战斗房间协议
│   │   ├── message.go            # 消息类型→结构体 注册表
│   │   └── ...
│   ├── xcard_msg_def/            # 自定义消息（登录/心跳等，ID < 1000）
│   │   ├── msg_const.go          # LoginReq=1, LoginResp=2, Ping=3, Pong=4
│   │   ├── client_msg.go         # LoginReq/LoginResp/Ping/Pong 结构体
│   │   └── msg_buf.go            # MsgBuf{MsgId, Msg, SeqID, Time}
│   ├── xcard_tcp/                # 网络层
│   │   ├── http_login.go         # HTTP 认证
│   │   ├── tcp_handler.go        # TCP 连接和消息收发
│   │   └── attr_sync_handler.go  # 服务端推送→SyncMap 自动同步
│   ├── xcard_net_lib/            # 消息编码/解码/压缩/加密
│   ├── xcard_case/               # 测试用例实现
│   │   ├── cases.go              # 用例注册表 RegisterCases()
│   │   ├── case_*.go             # 各功能测试用例
│   │   ├── module_login.go       # 登录模块
│   │   ├── module_gm.go          # GM 命令模块
│   │   └── easy_code.go          # 错误检查工具
│   ├── xcard_case_def/           # Case 接口定义
│   └── xcard_case_test/          # 单元测试目录
├── env/envSnapshot.go            # 环境变量读取
├── vars/                         # 全局变量
└── log_service/                  # 日志服务
```

Go module 名称：`git.devcloud.ztgame.com/v-tangfangda/rain-robot`

## 第二步：了解 proto 协议体系

### Proto 源文件位置

proto 源文件在 `D:\work\proto\` 目录下：

| 文件 | 内容 |
|------|------|
| `module/msgId.proto` | 消息 ID 枚举 `EGameMsgID`，注释标注方向（c-->s / s-->c） |
| `module/lobby.proto` | 大厅协议（GM、角色、好友、工会、邮件、排行榜等） |
| `module/room.proto` | 战斗房间协议（匹配、选将、出牌、战斗结算） |
| `module/match.proto` | 匹配系统 |
| `module/guild.proto` | 工会系统 |
| `module/guildcity.proto` | 工会城池 |
| `module/activity.proto` | 活动系统 |
| `module/friend.proto` | 好友系统 |
| `module/rougeEndLess.proto` | 肉鸽（PVE） |
| `module/chat.proto` | 聊天 |
| `common/enum.proto` | 枚举定义 |
| `common/common.proto` | 公共结构 |
| `common/userdata.proto` | 用户数据结构 |

### 消息 ID 体系

两套消息 ID 共存：

| 类型 | ID 范围 | 定义位置 | 示例 |
|------|---------|----------|------|
| 自定义消息 | 1-999 | `xcard_msg_def/msg_const.go` | LoginReq=1, LoginResp=2, Ping=3, Pong=4 |
| Proto 消息 | 1000+ | `xcard_pb/msgId.pb.go` | GmCommandReq=1001, HelloReq=1004 |

Proto 消息 ID 的命名规则：`EGameMsgID_{MessageName}_id`，其中 MessageName 去掉了 Req/Ack/Ntf 后缀。

### 消息命名约定

从 `msgId.proto` 的注释可以判断消息方向：

```protobuf
GmCommandReq_id = 1001;  // c-->s  客户端发给服务端
GmCommandAck_id = 1002;  // s-->c  服务端回客户端
RefreshUserDataNtf_id = 1016;  // s-->c  服务端主动推送
```

- **XxxReq** → 请求（c→s），对应 **XxxAck** → 响应（s→c）
- **XxxNtf** → 通知/推送（s→c），无对应响应

### Proto 编译与导入

项目使用 `gogofaster` 生成 Go 代码。proto 编译产物已在 `xcard_pb/` 目录下，无需手动编译。

在 Go 代码中引用 proto 类型：

```go
import protoMsg "git.devcloud.ztgame.com/v-tangfangda/rain-robot/project/xcard/xcard_pb"

// 使用 proto 结构体
req := &protoMsg.StartMatchReq{TeamType: 10005}
```

### 消息注册（关键！）

每个 proto 消息类型必须在 `xcard_pb/message.go` 的 `RegisterMsg` 中注册，否则框架无法反序列化：

```go
// message.go 中的注册格式
p.RegMsg(xcard_msg_def.MsgID(EGameMsgID_XxxReq_id), new(XxxReq))
```

如果新增了 proto 消息但忘记注册，`Wait()` 会因为无法反序列化而失败。

## 第三步：了解 TCP 通信细节

### 消息帧格式

每条 TCP 消息的编码格式（Little-Endian）：

```
[3字节 长度][1字节 标志位][2字节 MsgID][4字节 SeqID][N字节 序列化数据]
 ├─ MsgHeadSize=4 ─┤├─ MsgIDSize=2 ─┤├─ SeqSize=4 ─┤
```

- **长度**（3字节）：MsgID + SeqID + 序列化数据的总长度（不含 Head 自身）
- **标志位**（1字节）：bit0=压缩标记，bit1=加密标记
- **MsgID**（2字节）：消息 ID
- **SeqID**（4字节）：序列号，每发送一条 +1
- **序列化数据**：消息的序列化数据（见下方 ByteStream 说明）

编码实现在 `xcard_net_lib/encode_msg.go`，解码在 `xcard_net_lib/decode_msg.go`。

### ByteStream 序列化包装（关键！）

**所有消息的 payload 都经过 ByteStream 格式包装**，不仅仅是裸 proto 或裸二进制。这是 `EncodeMsg` → `SerializeNewWithBuff` 的统一序列化流程：

```
帧: [Head 4B][MsgID 2B][SeqID 4B][payload]
                                  ↓
payload = ByteStream.Serialize(消息结构体)
```

**自定义消息（MsgID < 1000）**：按字段顺序直接写入 ByteStream 二进制格式：
- `string` → `[2字节长度LE][字符串内容]`
- `uint32` → `[4字节LE]`
- `uint64` → `[8字节LE]`
- `bool` → `[1字节 0/1]`
- `map` → `[2字节长度][key+value 交替]`
- `[]byte` → `[2字节长度][字节数据]`

**Proto 消息（MsgID >= 1000）**：先 `proto.Marshal()` 得到二进制，再用 ByteStream 的 `WriteBytes` 包装：
- Proto 结构体指针 → `[2字节长度LE][proto Marshal 二进制]`

这意味着**发送 proto 消息时，payload 不是裸 protobuf，而是前面多了 2 字节长度前缀**。同样，**接收 proto 消息时，需要先读取 2 字节长度前缀，再取后面的数据做 proto 反序列化**。

这套机制在 `xcard_msg_def/serialize.go` 的 `serialize()` 函数中统一处理，框架的 `Call/Wait` 已封装，但在 rain-robot 框架外独立实现通信时**必须手动处理这层包装**。

#### 独立实现示例（不依赖 rain-robot 框架时）

```go
// 发送 proto 消息：加 ByteStream 头
protoData, _ := req.Marshal()           // proto Marshal
wrapped := make([]byte, 2+len(protoData))
binary.LittleEndian.PutUint16(wrapped, uint16(len(protoData)))
copy(wrapped[2:], protoData)            // [2B长度][proto数据]

// 接收 proto 消息：去 ByteStream 头
protoLen := binary.LittleEndian.Uint16(payload)
protoData := payload[2 : 2+protoLen]
ack, _ := proto.Unmarshal(protoData)
```

### 加密与压缩

- 消息体 >100 字节时自动 snappy 压缩
- 消息体自动加密（XOR 加密）
- 框架的 `SendTcpMsg` 和 `ListenTcpMsg` 已封装编码/解码/压缩/加密，开发者只需关注 Call/Wait

### 心跳

登录成功后自动启动心跳协程，每 5 秒发送 `Ping`（MsgID=3），服务端回复 `Pong`（MsgID=4）。ctx 取消时自动停止。

## 第四步：了解登录流程

登录分两个阶段，`LoginModule` 封装了完整流程：

### 阶段1: HTTP 认证

```
POST http://{ServerIp}:{ServerPort}/authlogin
Body: {"accessToken":"123", "uid":"botName_1", "sdk":"FakeSDK", "platform":"Android"}
Response: {"code":0, "token":"xxx", "serverAddr":"10.254.114.204:18000"}
```

- `uid` = 机器人名称（全局唯一，决定登录哪个账号）
- `serverAddr` = TCP 游戏服务器地址（由 HTTP 服务器动态分配，不同于 HTTP 端口）

### 阶段2: TCP 游戏登录

```
→ LoginReq {Account, Token, UID, Version:"0.8.3001.1.1"}
← LoginResp {UID, Result, ErrStr}
```

新账号登录后：
```
← RefreshUserDataNtf {PlayerInfo=nil, Milli=0, IsHaveRole=false}  ← 新账号 dataLen 很小（~2B）
→ CreateRoleReq {RoleName, Gender=EGender_Man, ItemID=1020303, IsRandom=true}
← CreateRoleAck {ErrCode}
← RefreshUserDataNtf {PlayerInfo=完整数据, Milli, IsHaveRole=true}
← LoginServerMsgOverNtf  ← 角色创建成功后才会发
```

**新账号 vs 老账号的关键差异**：
- 新账号的 RefreshUserDataNtf 很小（dataLen≈2B），因为 PlayerInfo 为空、Milli 为 0，只有 `isHaveRole=false`
- 老账号的 RefreshUserDataNtf 很大（dataLen≈253B+），包含完整 PlayerInfo
- 新账号如果 CreateRole 失败，服务端**不会发送 LoginServerMsgOverNtf(1017)**
- CreateRoleReq 是 **proto 消息**（MsgID=1006），需要 protobuf 序列化 + ByteStream 包装
- `ItemID` 必须为 `1020303`（形象道具 ID），`IsRandom` 应为 `true`，`Gender` 为 `EGender_Man`（枚举值，通常=1）

### 登录后自动同步

`syncAttr()` 自动处理以下服务端推送并存入 SyncMap：

| 推送消息 | SyncMap Key | 数据类型 |
|----------|-------------|----------|
| RefreshUserDataNtf | `"PlayerInfo"` | `*protoMsg.PlayerInfo` |
| RefreshUserDataNtf | `"IsHaveRole"` | `bool` |
| UserItemListNtf | `"ItemList"` | `*protoMsg.UserItemListNtf` |
| UserHeroListNtf | `"HeroItemList"` | `[]*protoMsg.HeroInfo` |
| RoomNtf | `"RoomInfo"` | `*protoMsg.RoomInfo` |
| StartBattleNtf | `"StartBattleNtf"` | `*protoMsg.StartBattleNtf` |
| StartBattleNtf | `"PlayerIdHeroIdMap"` | `map[uint64]uint32` |
| CardPileNtf | `"Circle"` | 牌堆信息 |
| UpdatePropertyNtf | `"BattleProperty"` | 战斗属性 |

### LoginModule 签名

```go
// module_login.go:22
func LoginModule(c robot.Robot, needCreateRole bool, loginTimeout time.Duration,
    version string, roleNamingPolicy int, ctx context.Context, cancel context.CancelFunc) error
```

参数说明：
- `needCreateRole=true` — 新账号自动创建角色
- `roleNamingPolicy` — 角色名策略（`vars.SameRoleName`=与账号同名，`vars.RandomName`=随机中文）
- `version` — 固定 `"0.8.3001.1.1"`
- 登录完成后等待 `LoginServerMsgOverNtf`（MsgID=1017），表示服务端初始推送全部结束

## 第五步：登录后的常见业务流程

了解这些典型流程，有助于判断新用例需要哪些步骤。

### 数据准备流程

大多数用例在登录后需要 GM 命令准备数据：

```go
gm := &GMModule{}
gm.GMAddAllHeroModule(c, ctx, cancel)       // 确保 >=16 个武将
gm.GMAddLevelModule(c, 30, ctx, cancel)      // 确保等级 >= 30
gm.GMReq(c, "描述", "//AddItem 1000009 100000", true, ctx, nil)  // 添加物品
```

### 好友流程

```
登录 → FriendSearchReq(搜索目标) → FriendApplyReq(申请) → 对方 FriendAgreeReq(同意)
→ FriendListReq(列表) → FriendChatReq(聊天) → FriendGiftReq(送礼)
```

### 工会流程

```
登录 → GuildCreateReq(创建) → GetGuildListReq(列表) → GuildSearchReq(搜索)
→ GuildJoinReq(加入) → GuildQuitReq(退出)
```

### 匹配与战斗流程

```
数据准备(武将+分数) → StartMatchReq(开始匹配) → StartMatchAck(匹配结果)
→ Wait(ChooseBattleHeroNtf, 选将推送) → Wait(StartBattleNtf, 战斗开始)
→ 战斗中交互(出牌等) → GameOverRoomNtf 或 GM结束战斗
```

### PVE 肉鸽流程

```
登录 → GMRougeClear(清理进度) → GMRougeSetMaxLevel(设置难度)
→ 进入肉鸽 → 选路线 → 战斗 → 循环
```

## 第六步：Robot 接口 — 所有交互的核心

`robot/robot_i.go` 定义的 Robot 接口是测试脚本与服务器的唯一交互点：

### 消息交互

```go
// 发送消息（msg 必须是指针），返回发送时间
call, err := c.Call(&protoMsg.XxxReq{Field: value}, protoMsg.EGameMsgID_XxxReq_id)

// 等待指定消息，超时返回 error
wait, err := c.Wait(protoMsg.EGameMsgID_XxxAck_id, 60*time.Second, ctx)

// 等待多个消息中的任意一个
wait, err := c.WaitAny([]xcard_msg_def.MsgID{id1, id2}, 60*time.Second, ctx)

// 等待消息列表（按序）
msgs, err := c.WaitList([][]int{{id1}, {id2}}, 60*time.Second, ctx)
```

`wait` 是 `*xcard_msg_def.MsgBuf`，包含：
- `wait.Msg` — 消息体（需类型断言为具体 proto 类型）
- `wait.SeqID` — 序列号
- `wait.Time` — 接收时间

### 属性同步

```go
// 读取框架自动同步的数据
value := c.SyncMapGet("PlayerInfo")

// 手动存储数据
c.SyncMapSet("MyKey", myData)

// 注册自定义推送处理器（在 LoginModule 之前调用）
c.RegisterSyncHandler(func(c robot.Robot, msg interface{}) {
    switch ntf := msg.(type) {
    case *protoMsg.SomeNtf:
        c.SyncMapSet("SomeKey", ntf.SomeField)
    }
}, new(protoMsg.SomeNtf))
```

### 日志与打点

```go
c.Mark("发生了某事")                                    // 标记点，不计耗时
c.Record("操作成功", call, wait.Time)                    // 记录带耗时
c.GetFullName()                                         // 获取机器人全名
```

## 第七步：错误处理模式

### 三级错误检查

```go
// Level 1: 只检查 Wait 是否出错（超时/断连）
if !CheckWaitMsgErr(c, "MsgName", err) {
    return
}

// Level 2: 检查 Wait 错误 + 响应中的 ErrCode（最常用）
if !CheckAckMsgErrCodeAndRecord[*protoMsg.XxxAck](c, "XxxAck", call, wait, err) {
    return
}

// Level 3: 检查 ErrCode + 出错时执行自定义回调
if !CheckWaitMsgErrCodeAndDoFuncThenRecord[*protoMsg.XxxAck](c, "XxxAck", call, wait, err, func(errCode uint32) {
    // 处理特定错误码
}) {
    return
}
```

错误码含义：`ErrCode == 0` = 成功。非零值可通过 `excel.EErrorCode_name[int32(errCode)]` 查找描述。

## 第八步：GM 命令系统

### 协议

- 请求：`GmCommandReq`（MsgID=1001），`Content` 字段为命令字符串，`PlayerID` 为目标玩家（0=自己）
- 响应：`GmCommandAck`（MsgID=1002），`ErrCode` 为错误码

### GMModule 用法

```go
gm := &GMModule{}

// needWait=true: 发送并等待 Ack（大多数场景）
gm.GMReq(c, "描述", "//AddItem 1000009 100000", true, ctx, nil)

// needWait=false: 发送不等 Ack（异步命令如开战）
gm.GMReq(c, "描述", "//GameOverRoomWin", false, ctx, nil)

// 带回调：发送后、等待前执行额外操作
gm.GMReq(c, "描述", "//AddHeroSkill 1015", true, ctx, func() {
    // hook 操作
})

// 指定目标玩家
gm.GMReq(c, "描述", "//AddItem 1000001 100", true, ctx, nil, targetPlayerID)
```

### 常用 GM 命令速查

| 命令 | 用途 | 示例 |
|------|------|------|
| `//AddItem <物品ID> <数量>` | 添加物品 | `//AddItem 1000009 100000` |
| `//AddAllItem <数量>` | 添加所有物品 | `//AddAllItem 10000000` |
| `//AddAllHero` | 添加所有武将 | `//AddAllHero` |
| `//Godmode` | 无敌模式 | `//Godmode` |
| `//SetArenaScore <分数>` | 设置竞技场分数 | `//SetArenaScore 10000` |
| `//StartRoomGame <人数>\|<武将ID列表>` | GM开战 | `//StartRoomGame 2\|101,102` |
| `//SetRoomTime <毫秒>` | 设置操作时间 | `//SetRoomTime 999999` |
| `//GameOverRoomWin` | GM赢得战斗 | `//GameOverRoomWin` |
| `//AddCardById <卡ID> <数量>` | 添加卡牌 | `//AddCardById 2027 50` |
| `//AddHeroSkill <技能ID>` | 添加武将技能 | `//AddHeroSkill 1015` |
| `//SendMail <邮件ID>` | 发送邮件 | `//SendMail 1001` |
| `//RougeClear` | 清理肉鸽进度 | `//RougeClear` |
| `//RougeSetMaxLevel <难度>` | 设置肉鸽难度 | `//RougeSetMaxLevel 5` |
| `//ClearEscapePunish` | 清除逃跑惩罚 | `//ClearEscapePunish` |
| `//AddRank <排行ID> <分数>` | 添加排行榜分 | `//AddRank 1 100` |
| `//DelRank <排行ID>` | 删除排行榜数据 | `//DelRank 1` |
| `//CustomBattle <参数>` | 自定义战斗 | `//CustomBattle ...` |

完整列表见 `project/xcard/login_flow_guide.txt` 第十八章。

## 第九步：编写测试用例的完整流程

### 确认需求

向用户确认（缺少任何一项都应询问）：

1. **测试什么功能** — 具体游戏功能
2. **是否需要多机器人协作** — 单人还是多人
3. **是否需要 GM 命令准备数据** — 添加武将、物品、等级等
4. **预期结果** — 成功表现、失败错误码

### 查找 proto 消息

编码前必须确认消息存在：

1. `codegraph_search` 搜索消息名（如 `StartMatchReq`）
2. 确认 MsgID 常量存在（如 `EGameMsgID_StartMatchReq_id`）
3. 读取 proto 结构体确认字段
4. 确认 `message.go` 中已注册该消息类型

如 proto 不存在，先用 `sync-rain-robot-pb` skill 同步。

### 创建文件

#### 文件 1: 用例实现 `project/xcard/xcard_case/case_{name}.go`

```go
package xcard_case

import (
	"context"
	"fmt"
	"time"

	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/env"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/log_service"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/project/xcard/xcard_excel/excel"
	protoMsg "git.devcloud.ztgame.com/v-tangfangda/rain-robot/project/xcard/xcard_pb"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/robot"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/vars"
)

// {CaseName} {功能描述}
type {CaseName} struct{}

// Logic 用例入口，实现 Case 接口
func (t *{CaseName}) Logic(c robot.Robot, envSnapshot *env.EnvVars, ctx context.Context, cancel context.CancelFunc) {
	// 1. 登录
	err := LoginModule(c, true, 60*time.Second, "0.8.3001.1.1", vars.SameRoleName, ctx, cancel)
	if err != nil {
		return
	}

	// 2. 数据准备（可选）
	gm := &GMModule{}
	// gm.GMAddAllHeroModule(c, ctx, cancel)

	// 3. 业务逻辑
	// call, _ := c.Call(&protoMsg.XxxReq{...}, protoMsg.EGameMsgID_XxxReq_id)
	// wait, err := c.Wait(protoMsg.EGameMsgID_XxxAck_id, 60*time.Second, ctx)
	// if !CheckAckMsgErrCodeAndRecord[*protoMsg.XxxAck](c, "XxxAck", call, wait, err) {
	//     return
	// }
}
```

#### 文件 2: 注册用例 `project/xcard/xcard_case/cases.go`

在 `RegisterCases` 中添加：

```go
p.RegCase("{CaseName}", {CaseName}{})
```

#### 文件 3: 单元测试 `project/xcard/xcard_case_test/client_{name}_test.go`

```go
package xcard_case_test

import (
	"context"
	"testing"
	"time"

	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/env"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/project/xcard/xcard_case"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/project/xcard/xcard_client"
	"git.devcloud.ztgame.com/v-tangfangda/rain-robot/vars"
	"github.com/stretchr/testify/assert"
)

func Test{FeatureName}(t *testing.T) {
	vars.UseOLAP = false
	vars.ServerIp = "10.254.114.204"
	vars.ServerPort = "20144"
	vars.TLSEnabled = false

	c := xcard_client.NewClientXCard("test{FeatureName}", 1, 1)
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()

	case_ := &xcard_case.{CaseName}{}
	case_.Logic(c, env.NewEnvVars(map[string]string{}), ctx, cancel)

	assert.NotNil(t, c.SyncMapGet("PlayerInfo"), "登录后应有 PlayerInfo")
}
```

#### 文件 4: 用例文档 `../../机器人项目/测试用例/{CaseName}.md`

按 `机器人项目/测试用例/CLAUDE.md` 规范和 `template.md` 模板编写。

### 验证

```powershell
# PowerShell 中（必须设置 GOOS）
$env:GOOS="windows"; $env:CGO_ENABLED="0"; go test -v -run Test{FeatureName} -timeout 180s ./project/xcard/xcard_case_test/
```

## 第十步：环境变量与运行模式

### 压测模式（多机器人并发）

```bash
export CASE=MyCase BOT_NUM=1000 PREFIX=test DESC=测试 LOG_LEVEL=2 LOGIN_TIME=60
./rain-robot
```

| 变量 | 说明 | 默认值 |
|------|------|--------|
| CASE | 用例名称 | TestCase |
| BOT_NUM | 每进程机器人数 | 1000 |
| PROCESS_NUM | 进程数 | 1 |
| PREFIX | 机器人名前缀 | test |
| LOGIN_TIME | 登录超时(秒) | 60 |

### 单元测试模式

用例代码中通过 `envSnapshot` 读取参数：

```go
botNum := envSnapshot.GetEnvInt("CASE_BOT_NUM", vars.BotNum)
qps := envSnapshot.GetEnvFloat("QPS", -1)
```

## 常见陷阱

1. **GOOS=linux**: 本机默认 GOOS 是 linux，必须 PowerShell 设置 `$env:GOOS="windows"`
2. **ClickHouse 阻塞**: `vars.UseOLAP = false` 必须在测试启动前设置
3. **消息未注册**: 新增 proto 类型必须在 `xcard_pb/message.go` 的 `RegisterMsg` 中注册
4. **Call 的 msg 必须是指针**: `&protoMsg.XxxReq{}` 不能漏掉 `&`
5. **Ctx 超时**: 始终用 `context.WithTimeout` 防止测试永远挂起
6. **Wait 超时**: 单次 Wait 建议 60 秒，Ntf 类消息可能需要更长
7. **Proto 消息的 ByteStream 包装**: 独立实现通信时，proto 消息 payload 不是裸 protobuf，而是 `[2字节长度LE][protobuf二进制]`。发送要加前缀，接收要去前缀再反序列化。框架内 `Call/Wait` 已自动处理
8. **CreateRoleReq 是 proto 消息不是自定义消息**: MsgID=1006 >= 1000，属于 proto 消息，需要 protobuf 序列化 + ByteStream 包装，不能用自定义二进制格式。且 `ItemID` 必须为 `1020303`（不是 0），`IsRandom` 应为 `true`
9. **消息消费竞争**: 如果用 channel 分发消息，多个消费者竞争消费会导致消息丢失。应使用统一的消费循环，在一个循环内根据 MsgID 分发处理
10. **HTTP 登录 JSON 字段名**: 请求体使用下划线风格（`access_token`、`server_addr`），不是驼峰
11. **心跳必须启动**: 登录成功后不启动心跳，服务端会在约 10 秒后断开连接
12. **新账号 LoginServerMsgOverNtf 可能不发**: 新账号如果 CreateRole 失败（参数错误），服务端不会发 1017。如果 1017 超时，检查 CreateRole 流程是否正确

## 代码位置索引

| 组件 | 位置 |
|------|------|
| Robot 接口 | `robot/robot_i.go` |
| Case 接口 | `project/xcard/xcard_case_def/case_i.go:9` |
| 用例注册 | `project/xcard/xcard_case/cases.go:7` |
| 登录模块 | `project/xcard/xcard_case/module_login.go:22` |
| GM 模块 | `project/xcard/xcard_case/module_gm.go:14` |
| 错误检查工具 | `project/xcard/xcard_case/easy_code.go` |
| 消息帧编解码 | `project/xcard/xcard_net_lib/encode_msg.go` / `decode_msg.go` |
| ByteStream 序列化 | `project/xcard/xcard_msg_def/serialize.go`（统一处理自定义消息和 proto 消息的序列化） |
| 帧格式常量 | `project/xcard/xcard_net_lib/corder.go`（MsgHeadSize=4, MsgIDSize=2, SeqSize=4） |
| XOR 加密密钥 | `project/xcard/xcard_net_lib/key.go`（encryptKey/decryptKey 各 8 字节） |
| XOR 加密算法 | `project/xcard/xcard_net_lib/encrypt.go`（循环左移 + XOR） |
| HTTP 登录 | `project/xcard/xcard_tcp/http_login.go:73` |
| TCP 收发 | `project/xcard/xcard_tcp/tcp_handler.go`（`SendTcpMsg` → `EncodeMsg` → `CompressAndEncrypt` → `sendData`） |
| 属性同步 | `project/xcard/xcard_tcp/attr_sync_handler.go` |
| Proto 消息 ID | `project/xcard/xcard_pb/msgId.pb.go` |
| Proto 结构体 | `project/xcard/xcard_pb/lobby.pb.go` |
| 消息注册表 | `project/xcard/xcard_pb/message.go` |
| Proto 源文件 | `D:\work\proto\module\*.proto` |
| 登录流程详解 | `project/xcard/login_flow_guide.txt` |

## 独立开发路径（不依赖 rain-robot 框架）

rain-robot 框架的 proto 编译产物（`xcard_pb/`）本身就来自服务端 proto 源文件。因此可以跳过 rain-robot 框架，**直接从服务端 proto 源文件用 buf 构建独立项目**，实现自己的机器人脚本或工具。

### 路径对比

```
路径 A: 在 rain-robot 框架内开发（本 skill 前九步描述的方式）
  proto → gogofaster → xcard_pb/ → import → 测试用例
  优点：框架提供 Call/Wait/LoginModule/GMModule 全套工具
  适合：标准测试用例开发

路径 B: 独立项目（本节描述）
  D:\work\proto\ → buf generate → 自己的 gen/ → 独立程序
  优点：零框架依赖，可以做成 CLI 工具、HTTP 服务等
  适合：GM 工具、调试工具、自定义压测脚本
```

### 独立开发需要自己实现的组件

| 组件 | 说明 | 参考实现 |
|------|------|----------|
| HTTP 登录 | POST `/authlogin`，获取 token + TCP 地址 | `xcard_tcp/http_login.go` |
| TCP 帧编解码 | 4B头 + MsgID + SeqID + payload | `xcard_net_lib/encode_msg.go` / `decode_msg.go` |
| XOR 加密 | 循环左移 + XOR，密钥在 `key.go` | `xcard_net_lib/encrypt.go` + `key.go` |
| Snappy 压缩 | payload >100 字节时压缩 | `xcard_net_lib/encode_msg.go` |
| ByteStream 序列化 | proto 消息加 2B 长度前缀 | 本 skill 第三步 ByteStream 章节 |
| 心跳 | 每 5 秒 Ping(MsgID=3) | `xcard_tcp/tcp_handler.go` |
| 自定义消息序列化 | LoginReq 等按字段顺序二进制编码 | `xcard_msg_def/serialize.go` |

### Proto 构建方式

proto 源文件在 `D:\work\proto\`，可用以下方式生成 Go 代码：

**方式 1: buf generate（推荐）**
```yaml
# buf.yaml
version: v2
modules:
  - path: proto
```
```yaml
# buf.gen.yaml
version: v2
managed:
  enabled: true
  override:
    - file_option: go_package_prefix
      value: "your-module/gen"
plugins:
  - remote: buf.build/protocolbuffers/go
    out: gen
    opt: paths=source_relative
```
注意：需要处理 proto 文件间的 import 依赖（lobby.proto import 了 room.proto、enum.proto 等）。

**方式 2: 手写 protowire 编解码（少量消息时更简洁）**

只用到几个消息时，可以用 `google.golang.org/protobuf/encoding/protowire` 手动编码/解码，跳过 proto 文件和 buf 工具。gm-tool 就是这种方式。

**proto 生成插件不影响协议兼容性**：rain-robot 用 `gogofaster`，独立项目可以用标准 `protoc-gen-go`。TCP 线上传输的是标准 protobuf wire format，跟生成插件无关。

### 完整的独立开发示例

已有一个可运行的独立项目 `cmd/gm-tool/`，使用 cobra CLI，成功连接 204 服务器执行 GM 命令。项目结构：

```
cmd/gm-tool/
├── main.go              # cobra CLI 入口
├── go.mod               # 独立 go module
├── gen/gm.pb.go         # 手写 protowire 编解码（GmCommandReq/Ack）
└── internal/
    ├── auth/auth.go     # HTTP 登录
    ├── net/crypto.go    # TCP 帧编解码 + XOR 加密 + Snappy 压缩
    └── gm/client.go     # TCP 登录流程 + GM 命令发送
```

该项目的关键实现经验：
- 自定义消息（LoginReq）用 ByteStream 二进制序列化，proto 消息用 protobuf 序列化后再加 2 字节长度前缀
- 接收 proto 消息时也要先去掉 2 字节长度前缀再反序列化
- 心跳必须在登录后启动，否则服务端约 10 秒后断连
- 登录流程要等待 LoginServerMsgOverNtf(1017) 后才能执行业务操作

## 已知限制

以下是尚未完全确认或需要服务端配合排查的问题：

| 问题 | 现象 | 状态 |
|------|------|------|
| `//Godmode` 返回 errCode=1001 | 三个独立项目都返回此错误，其他 GM 命令正常 | 待确认是否为服务端 GM 命令格式变更或需要前置条件 |
| 新账号创建角色后仍收到 `hasRole=false` | CreateRoleReq 发出后没收到 CreateRoleAck(1007) | 已确认参数错误（ItemID 应为 1020303 而非 0），修正后需重新验证 |
| LoginReq 后收到未知消息 MsgID=5050/1200/6500 | 登录流程中出现未识别的推送消息 | 不影响功能，可能是服务端的额外系统推送（版本检查、公告等） |

### 已验证通过的 GM 命令

| 命令 | 结果 |
|------|------|
| `//AddAllHero` | errCode=0，成功 |
| `//AddItem <物品ID> <数量>` | 格式已验证（具体 ID 需测试） |
| `//Godmode` | errCode=1001，待排查 |
