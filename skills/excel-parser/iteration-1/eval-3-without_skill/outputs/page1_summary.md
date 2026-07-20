# Hero 表第 1 页数据（第 1-20 行）

**文件路径**: `D:\work\config\excel\Hero.xlsx`  
**Sheet 名称**: 武将表|Hero  
**数据行数**: 20 行  

## 列名表头（共 23 列）

| 序号 | 中文名称 | 字段名 | 类型 | 导出标记 |
|------|----------|--------|------|----------|
| 1 | 武将ID | Id | EHeroId | server/client |
| 2 | 武将名称 | Name | string | server/client |
| 3 | (空) | | E#EHeroId | |
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
| 17 | (空) | | E#EHeroType | |
| 18 | 是否能熔炼 | CanMelt | bool | server/client |
| 19 | 熔炼名称 | MeltName | string[] | server/client |
| 20 | 是否为新增武将 | IsNewHero | bool | client |
| 21 | 是否招募产出 | IsGacha | bool | client |
| 22 | 所属扩展包 | BelongExpansionPack | EHeroExpansionPackType | server/client |
| 23 | Buff ID | Buff | EBuffId[] | server |

## 数据预览（前 20 行）

| 行号 | 武将ID | 武将名称 | 英文名 | 是否开放 | 性别 | 初始体力 | 体力上限 | 手牌上限 | 装备上限 | 国号 | 技能 ID |
|------|--------|----------|--------|----------|------|----------|----------|----------|----------|------|----------|
| 1 | 1000 | 熔炼武将ID局外 | MeltHero | | | | | | | | |
| 2 | 1001 | 局内1号位 | MeltHeroPos1 | | | | | | | | |
| 3 | 1002 | 局内2号位 | MeltHeroPos2 | | | | | | | | |
| 4 | 1003 | 局内3号位 | MeltHeroPos3 | | | | | | | | |
| 5 | 1004 | 局内4号位 | MeltHeroPos4 | | | | | | | | |
| 6 | 1005 | 局内5号位 | MeltHeroPos5 | | | | | | | | |
| 7 | 1006 | 局内6号位 | MeltHeroPos6 | | | | | | | | |
| 8 | 1007 | 局内7号位 | MeltHeroPos7 | | | | | | | | |
| 9 | 1008 | 局内8号位 | MeltHeroPos8 | | | | | | | | |
| 10 | 1009 | 召唤物阵亡座位 | MeltHeroPos9 | | | | | | | | |
| 11 | 10001 | 曹操 | CaoCao | 1 | 1 | 5 | 5 | 4 | 3 | CaoWei | 1001,1074,1075 |
| 12 | 10002 | 郭嘉 | GuoJia | 1 | 1 | 4 | 4 | 5 | 3 | CaoWei | 1004,1005,1006 |
| 13 | 10003 | 夏侯惇 | XiaHouDun | 1 | 1 | 6 | 6 | 3 | 3 | CaoWei | 1007,1008 |
| 14 | 10004 | 张辽 | ZhangLiao | 1 | 1 | 6 | 6 | 3 | 3 | CaoWei | 1009,1010 |
| 15 | 10005 | 甄宓 | ZhenFu | 1 | 2 | 4 | 4 | 4 | 3 | CaoWei | 1011,1012 |
| 16 | 10006 | 司马懿 | SiMaYi | 1 | 1 | 4 | 4 | 5 | 3 | CaoWei | 1013,1014 |
| 17 | 10007 | 典韦 | DianWei | 1 | 1 | 6 | 6 | 3 | 3 | CaoWei | 1064,1065 |
| 18 | 10008 | 许褚 | XuZhu | 1 | 1 | 6 | 6 | 3 | 3 | CaoWei | 1068,1069 |
| 19 | 10009 | 荀彧 | XunYu | 1 | 1 | 4 | 4 | 5 | 3 | CaoWei | 1310,1311,1312 |
| 20 | 10010 | 曹仁 | CaoRen | 1 | 1 | 6 | 6 | 3 | 3 | CaoWei | 1110,1111,1112 |

**说明**:
- 第 1-10 行是熔炼武将的特殊配置（用于熔炼系统）
- 第 11-20 行是曹魏势力的武将数据
