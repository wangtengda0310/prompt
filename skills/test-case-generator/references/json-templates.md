# JSON 测试模板参考

## 战斗测试用例模板（rain-qa-func）

### Schema 位置

`rain-qa-func/cases/fight_cases_schema.json`

### 基本结构

```json
[
  {
    "case": "武将名_技能名_01",
    "desc": "测试武将X的技能Y在Z场景下的表现",
    "manager": "负责人名",
    "initYanWu": {
      "presentId": 0,
      "cardPile": 0,
      "cards": [1003, 1082],
      "operateTimeMs": 30000,
      "customHeroes": [
        {
          "identity": 13,
          "color": 97,
          "heroId": 10002,
          "initCards": [1123, 1042],
          "initEquips": [],
          "augurCards": [],
          "addSkills": [1381],
          "delSkills": [1004, 1005],
          "exEquips": [],
          "skillCardsMap": {}
        }
      ]
    },
    "steps": [
      {
        "id": 1,
        "desc": "步骤描述：执行某个操作",
        "robotIdx": 1,
        "action": "PlayCard",
        "cardId": 1003,
        "confirm": false,
        "timeout": 1,
        "assets": [
          {
            "msgName": "PlayCardAck",
            "desc": "出牌应返回成功",
            "attr": {"Result": "0"}
          }
        ]
      }
    ]
  }
]
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case | string | 是 | 用例唯一标识，格式建议：武将名_技能名_序号 |
| desc | string | 否 | 用例描述 |
| manager | string | 否 | 负责人 |
| initYanWu | object | 是 | 初始化配置 |
| initYanWu.presentId | int | 是 | 场景ID |
| initYanWu.cardPile | int | 是 | 牌堆类型 |
| initYanWu.cards | int[] | 是 | 初始牌堆卡牌ID列表 |
| initYanWu.operateTimeMs | int | 是 | 操作超时时间(毫秒) |
| initYanWu.customHeroes | object[] | 是 | 自定义英雄配置 |
| steps | object[] | 是 | 执行步骤列表 |

### Step 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 步骤序号 |
| desc | string | 否 | 步骤描述 |
| robotIdx | int | 否 | 执行操作的机器人序号（多机器人场景） |
| action | string | 是 | 动作类型 |
| cardId | int | 否 | 出牌动作的卡牌ID |
| confirm | bool | 否 | 是否需要确认 |
| timeout | int | 否 | 超时时间(秒) |
| assets | object[] | 否 | 断言列表 |

### Action 类型

| Action | 说明 |
|--------|------|
| PlayCard | 出牌 |
| OptRoomAction | 场景操作 |
| UseHeroSkill | 使用武将技能 |
| OnlyAsset | 仅等待断言（不做操作） |

### Asset 断言格式

```json
{
  "msgName": "Ack消息名",
  "desc": "断言描述",
  "attr": {
    "字段名": "期望值"
  }
}
```

### 多机器人场景

```json
{
  "case": "双人对战_基础",
  "initYanWu": {
    "presentId": 0,
    "cardPile": 0,
    "cards": [1001, 1002],
    "operateTimeMs": 30000,
    "customHeroes": [
      {
        "identity": 1,
        "heroId": 10001,
        "initCards": [1001],
        "initEquips": [],
        "addSkills": [],
        "delSkills": [],
        "augurCards": [],
        "exEquips": [],
        "skillCardsMap": {}
      },
      {
        "identity": 2,
        "heroId": 10002,
        "initCards": [1002],
        "initEquips": [],
        "addSkills": [],
        "delSkills": [],
        "augurCards": [],
        "exEquips": [],
        "skillCardsMap": {}
      }
    ]
  },
  "steps": [
    {"id": 1, "robotIdx": 1, "action": "PlayCard", "cardId": 1001, "assets": []},
    {"id": 2, "robotIdx": 2, "action": "PlayCard", "cardId": 1002, "assets": [
      {"msgName": "PlayCardAck", "desc": "对方出牌后应收到通知", "attr": {"Result": "0"}}
    ]}
  ]
}
```
