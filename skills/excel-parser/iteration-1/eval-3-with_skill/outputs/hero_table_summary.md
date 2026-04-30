# 武将表（Hero）数据分页查看

## 数据源信息

- **文件路径**: `D:/work/config/excel/Hero.xlsx`
- **Sheet 名称**: `武将表|Hero`
- **总数据行**: 40+ 行
- **本次查询**: 第1-40行（分2页展示）

---

## 第1页（第1-20行）

### 页面统计
- **数据条数**: 20 条
- **包含势力**: 曹魏
- **特殊数据**: 10条熔炼武将ID

### 列名表头

| 列序号 | 中文名称 | 字段名 | 类型 | 导出标识 |
|:------:|----------|--------|------|----------|
| 1 | 武将ID | Id | EHeroId | server/client |
| 2 | 武将名称 | Name | string | server/client |
| 3 | （枚举列） | | E#EHeroId | |
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
| 17 | （枚举列） | | E#EHeroType | |
| 18 | 是否能熔炼 | CanMelt | bool | server/client |
| 19 | 熔炼名称 | MeltName | string[] | server/client |
| 20 | 是否为新增武将 | IsNewHero | bool | client |
| 21 | 是否招募产出 | IsGacha | bool | client |
| 22 | 所属扩展包 | BelongExpansionPack | EHeroExpansionPackType | server/client |
| 23 | Buff ID | Buff | EBuffId[] | server |

### 数据预览（精选字段）

| 行号 | 武将ID | 武将名称 | 字段名 | 国号 | 体力 | 技能数 |
|:----:|:------:|:--------:|:--------|:------|:----:|:------:|
| 1 | 1000 | 熔炼武将ID局外 | MeltHero | | | |
| 2 | 1001 | 局内1号位 | MeltHeroPos1 | | | |
| 3 | 1002 | 局内2号位 | MeltHeroPos2 | | | |
| 4 | 1003 | 局内3号位 | MeltHeroPos3 | | | |
| 5 | 1004 | 局内4号位 | MeltHeroPos4 | | | |
| 6 | 1005 | 局内5号位 | MeltHeroPos5 | | | |
| 7 | 1006 | 局内6号位 | MeltHeroPos6 | | | |
| 8 | 1007 | 局内7号位 | MeltHeroPos7 | | | |
| 9 | 1008 | 局内8号位 | MeltHeroPos8 | | | |
| 10 | 1009 | 召唤物阵亡座位 | MeltHeroPos9 | | | |
| 11 | 10001 | 曹操 | CaoCao | CaoWei | 5 | 3 |
| 12 | 10002 | 郭嘉 | GuoJia | CaoWei | 4 | 3 |
| 13 | 10003 | 夏侯惇 | XiaHouDun | CaoWei | 6 | 2 |
| 14 | 10004 | 张辽 | ZhangLiao | CaoWei | 6 | 2 |
| 15 | 10005 | 甄宓 | ZhenFu | CaoWei | 4 | 2 |
| 16 | 10006 | 司马懿 | SiMaYi | CaoWei | 4 | 2 |
| 17 | 10007 | 典韦 | DianWei | CaoWei | 6 | 2 |
| 18 | 10008 | 许褚 | XuZhu | CaoWei | 6 | 2 |
| 19 | 10009 | 荀彧 | XunYu | CaoWei | 4 | 3 |
| 20 | 10010 | 曹仁 | CaoRen | CaoWei | 6 | 3 |

---

## 第2页（第21-40行）

### 页面统计
- **数据条数**: 20 条
- **包含势力**: 曹魏（6人）、蜀汉（14人）
- **主公数量**: 1人（刘备）

### 数据预览（精选字段）

| 行号 | 武将ID | 武将名称 | 字段名 | 国号 | 体力 | 技能数 |
|:----:|:------:|:--------:|:--------|:------|:----:|:------:|
| 21 | 10011 | 张春华 | ZhangChunHua | CaoWei | 4 | 2 |
| 22 | 10012 | 王异 | WangYi | CaoWei | 4 | 2 |
| 23 | 10013 | 曹丕 | CaoPi | CaoWei | 5 | 3 |
| 24 | 10014 | 曹植 | CaoZhi | CaoWei | 4 | 2 |
| 25 | 10015 | 徐晃 | XuHuang | CaoWei | 6 | 2 |
| 26 | 10016 | 张郃 | ZhangHe | CaoWei | 6 | 3 |
| 27 | 10101 | 刘备 | LiuBei | Shu | 5 | 3 |
| 28 | 10102 | 诸葛亮 | ZhuGeLiang | Shu | 4 | 2 |
| 29 | 10103 | 关羽 | GuanYu | Shu | 6 | 3 |
| 30 | 10104 | 张飞 | ZhangFei | Shu | 6 | 3 |
| 31 | 10105 | 赵云 | ZhaoYun | Shu | 6 | 3 |
| 32 | 10106 | 马超 | MaChao | Shu | 6 | 2 |
| 33 | 10107 | 黄忠 | HuangZhong | Shu | 6 | 3 |
| 34 | 10108 | 孙尚香 | SunShangXiang | Shu | 4 | 2 |
| 35 | 10109 | 姜维 | JiangWei | Shu | 6 | 3 |
| 36 | 10110 | 刘禅 | LiuShan | Shu | 5 | 2 |
| 37 | 10111 | 黄月英 | HuangYueYing | Shu | 4 | 2 |
| 38 | 10112 | 魏延 | WeiYan | Shu | 6 | 3 |
| 39 | 10113 | 法正 | FaZheng | Shu | 4 | 2 |
| 40 | 10114 | 庞统 | PangTong | Shu | 3 | 2 |

---

## 数据统计汇总

### 势力分布（前40行）

| 势力 | 人数 | 占比 |
|:----:|:----:|:----:|
| 熔炼武将 | 10 | 25% |
| 曹魏 | 16 | 40% |
| 蜀汉 | 14 | 35% |

### 体力分布

| 体力值 | 人数 | 说明 |
|:------:|:----:|:------|
| 3 | 1 | 庞统 |
| 4 | 12 | 文官型武将 |
| 5 | 4 | 主公型武将 |
| 6 | 23 | 武将型武将 |

### 性别分布

| 性别 | 人数 | 占比 |
|:----:|:----:|:----:|
| 男（1） | 36 | 90% |
| 女（2） | 4 | 10% |

### 武将状态

| 状态 | 人数 | 说明 |
|:----:|:----:|:------|
| 已开放 | 36 | 可正常使用 |
| 未开放 | 4 | 王异、刘禅、黄月英、魏延 |

### 主公武将

| 武将ID | 武将名称 | 势力 | 所在页 |
|:------:|:--------:|:------|:------:|
| 10001 | 曹操 | 曹魏 | 第1页 |
| 10101 | 刘备 | 蜀汉 | 第2页 |

---

## 使用说明

### 分页计算公式

```
第N页起始行 = (N - 1) × 每页行数 + 1
第N页结束行 = N × 每页行数

例如（每页20行）：
- 第1页：第1-20行
- 第2页：第21-40行
- 第3页：第41-60行
```

### 查询更多数据

如需查看第3页及以后的数据，请使用：

```bash
# 获取第3页（第41-60行）
preview_excel_sheet(filePath="D:/work/config/excel/Hero.xlsx", sheetName="武将表|Hero", rows=60)
```

然后手动提取第41-60行的数据。

---

## 生成信息

- **生成时间**: 2026-03-24
- **使用工具**: rain-qa-func MCP 服务
- **MCP工具**: `preview_excel_sheet`
- **数据格式**: JSON + Markdown
