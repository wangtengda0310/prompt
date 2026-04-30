# Hero 表分页查询任务总结

## 任务概述
成功获取 Hero 表的分页数据，每页包含 20 行数据（含列名表头）。

## 文件信息
- **文件路径**: `D:\work\config\excel\Hero.xlsx`
- **Sheet 名称**: 武将表|Hero
- **总列数**: 23 列

## 列名表头

| 序号 | 中文名称 | 字段名 | 类型 | 导出标记 |
|------|----------|--------|------|----------|
| 1 | 武将ID | Id | EHeroId | server/client |
| 2 | 武将名称 | Name | string | server/client |
| 3 | (空-枚举列) | | E#EHeroId | |
| 4 | 武将是否开放 | IsOpen | bool | server/client |
| 5 | 开放时间 | OpenDate | string | server/client |
| 6 | 性别 | Gender | int | server/client |
| 7 | 初始体力 | Point | int | server/client |
| 8 | 体力上限 | HpLimit | int | server/client |
| 9 | 手牌上限 | HandLimit | int | server/client |
| 10 | 装备上限 | EquipLimit | int | server/client |
| 11 | 国号 | Country | ECountry | server/client |
| 12 | 是否常备主公 | IsAlwaysZhuGong | bool | server/client |
| 13 | 技能 ID | Skill | ESkillId[] | server/client |
| 14 | 排除的身份枚举 | ExcludeIdentity | int[] | server |
| 15 | 不可以使用的房间模式 | NotUseModeType | EModeRuleType[] | server/client |
| 16 | 武将类型 | HeroType | EHeroType | server/client |
| 17 | (空-枚举列) | | E#EHeroType | |
| 18 | 是否能熔炼 | CanMelt | bool | server/client |
| 19 | 熔炼名称 | MeltName | string[] | server/client |
| 20 | 是否为新增武将 | IsNewHero | bool | client |
| 21 | 是否招募产出 | IsGacha | bool | client |
| 22 | 所属扩展包 | BelongExpansionPack | EHeroExpansionPackType | server/client |
| 23 | Buff ID | Buff | EBuffId[] | server |

## 第 1 页数据（第 1-20 行）

**数据行数**: 20 行

### 武将分布
- **行 1-10**: 熔炼武将特殊配置（用于熔炼系统的占位武将）
  - 武将ID: 1000-1009
  - 无实际战斗属性

- **行 11-20**: 曹魏势力武将
  - 曹操 (10001)、郭嘉 (10002)、夏侯惇 (10003)、张辽 (10004)、甄宓 (10005)
  - 司马懿 (10006)、典韦 (10007)、许褚 (10008)、荀彧 (10009)、曹仁 (10010)

## 第 2 页数据（第 21-40 行）

**数据行数**: 20 行

### 武将分布
- **行 21-26**: 继续曹魏势力武将
  - 张春华 (10011)、王异 (10012)、曹丕 (10013)、曹植 (10014)、徐晃 (10015)、张郃 (10016)

- **行 27-40**: 蜀势力武将
  - 刘备 (10101)、诸葛亮 (10102)、关羽 (10103)、张飞 (10104)、赵云 (10105)
  - 马超 (10106)、黄忠 (10107)、孙尚香 (10108)、姜维 (10109)、刘禅 (10110)
  - 黄月英 (10111)、魏延 (10112)、法正 (10113)、庞统 (10114)

## 输出文件

1. **page1_summary.md** - 第 1 页数据摘要（Markdown 格式）
2. **page2_summary.md** - 第 2 页数据摘要（Markdown 格式）
3. **page1_raw.json** - 第 1 页原始数据（JSON 格式）
4. **page2_raw.json** - 第 2 页原始数据（JSON 格式）
5. **final_summary.md** - 任务总结（本文件）

## 关键发现

1. **武将ID规则**:
   - 1000-1009: 熔炼系统占位武将
   - 10001-10999: 曹魏势力
   - 10101-10999: 蜀势力
   - 预计 10201-10999: 东吴势力

2. **未开放武将**（IsOpen = 0）:
   - 王异 (10012)
   - 刘禅 (10110)
   - 黄月英 (10111)
   - 魏延 (10112)

3. **性别分布**:
   - 1 = 男性
   - 2 = 女性

4. **势力分布**:
   - CaoWei: 曹魏
   - Shu: 蜀
