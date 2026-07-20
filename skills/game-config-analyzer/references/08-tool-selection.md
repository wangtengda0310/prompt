# 工具选择策略

本文档详细说明配表分析工具的选择策略。

## 目录

- [工具选择流程](#工具选择流程)
- [工具类型](#工具类型)
- [检测方法](#检测方法)
- [兼容性处理](#兼容性处理)

---

## 工具选择流程

### 选择优先级

```
┌─────────────────────────────────────────────────────────────┐
│  用户请求: "查询 Hero 表的配置"                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────────────┐
                │ 检测项目特定工具？            │
                │ - 检查 .gameconfig.yaml       │
                │ - 检查 scripts/ 目录          │
                └───────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │ Yes                       │ No
              ▼                           ▼
    ┌─────────────────┐       ┌───────────────────────┐
    │ 使用项目工具    │       │ 检测本地 MCP 服务？    │
    │ scripts/query   │       └───────────────────────┘
    └─────────────────┘                    │
                                  ┌───────────┴───────────┐
                                  │ Yes                   │ No
                                  ▼                       ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │ 使用 MCP 服务   │     │ 使用技能自带     │
                        │ (excel-parser等)│     │ analyzer.py     │
                        └─────────────────┘     └─────────────────┘
```

### 实现代码

```python
class ToolSelector:
    """工具选择器"""

    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.selected_tool = None
        self.tool_type = None

    def select_tool(self) -> Dict:
        """选择合适的工具"""
        # 1. 检查项目特定工具
        project_tool = self._check_project_tool()
        if project_tool:
            self.selected_tool = project_tool
            self.tool_type = "project"
            return project_tool

        # 2. 检查本地 MCP 服务
        mcp_tool = self._check_mcp_tool()
        if mcp_tool:
            self.selected_tool = mcp_tool
            self.tool_type = "mcp"
            return mcp_tool

        # 3. 使用技能自带脚本
        builtin_tool = self._get_builtin_tool()
        self.selected_tool = builtin_tool
        self.tool_type = "builtin"
        return builtin_tool

    def _check_project_tool(self) -> Dict:
        """检查项目特定工具"""
        # 检查 .gameconfig.yaml
        config_file = self.project_dir / ".gameconfig.yaml"
        if config_file.exists():
            return self._load_gameconfig(config_file)

        # 检查 pyproject.toml
        pyproject = self.project_dir / "pyproject.toml"
        if pyproject.exists():
            return self._load_pyproject_tool(pyproject)

        # 检查 scripts/ 目录
        scripts_dir = self.project_dir / "scripts"
        if scripts_dir.exists():
            # 查找配置相关脚本
            for script in ["query_config.py", "config_query.py", "analyze.py"]:
                script_path = scripts_dir / script
                if script_path.exists():
                    return {
                        "type": "project_script",
                        "command": "python",
                        "args": [str(script_path)],
                        "script": script
                    }

        return None

    def _check_mcp_tool(self) -> Dict:
        """检查本地 MCP 服务"""
        try:
            # 列出可用的 MCP 服务器
            mcp_servers = self._list_mcp_servers()

            # 查找配置相关的 MCP 服务
            config_mcps = [
                s for s in mcp_servers
                if any(kw in s.lower() for kw in ["excel", "config", "parser", "gameconfig", "game-meta"])
            ]

            if config_mcps:
                return {
                    "type": "mcp",
                    "servers": config_mcps
                }
        except Exception as e:
            pass  # MCP 不可用

        return None

    def _get_builtin_tool(self) -> Dict:
        """获取技能自带工具"""
        script_dir = Path(__file__).parent.parent / "scripts"
        analyzer_script = script_dir / "analyzer.py"

        return {
            "type": "builtin",
            "command": "python",
            "args": [str(analyzer_script)],
            "script": "analyzer.py"
        }
```

---

## 工具类型

### 1. 项目特定工具

**配置文件格式**：

#### YAML 格式 (`.gameconfig.yaml`)

```yaml
# .gameconfig.yaml
tools:
  query:
    command: "python"
    args: ["scripts/query_config.py", "{action}", "{table}"]
    description: "项目配置查询工具"

  modify:
    command: "python"
    args: ["scripts/modify_config.py", "{action}", "{table}"]
    description: "项目配置修改工具"

  validate:
    command: "python"
    args: ["scripts/validate_config.py"]
    description: "项目配置验证工具"

settings:
  encoding: "utf-8"
  excel_dir: "configs/excel"
  output_dir: "output"
```

#### TOML 格式 (`pyproject.toml`)

```toml
# pyproject.toml
[tool.gameconfig]
query-script = "scripts/query.py"
modify-script = "scripts/modify.py"
validate-script = "scripts/validate.py"

[tool.gameconfig.settings]
encoding = "utf-8"
excel-dir = "configs/excel"
output-dir = "output"
```

#### JSON 格式 (`.gameconfig.json`)

```json
{
  "tools": {
    "query": {
      "command": "python",
      "args": ["scripts/query.py", "{action}", "{table}"]
    },
    "modify": {
      "command": "python",
      "args": ["scripts/modify.py", "{action}", "{table}"]
    }
  },
  "settings": {
    "encoding": "utf-8",
    "excelDir": "configs/excel"
  }
}
```

### 2. MCP 服务

**常用 MCP 服务**：

| 服务名 | 功能 | 工具列表 |
|--------|------|----------|
| excel-parser | Excel 配表解析 | get_all_excels, get_excel_column_info |
| gameconfig | 游戏配置管理 | query, modify, validate |
| game-meta | 策划表操作 | export_csv, update |

**MCP 调用示例**：

```python
# 使用 excel-parser MCP 服务
def query_via_mcp(table_name: str) -> Dict:
    """通过 MCP 服务查询"""
    # 调用 MCP 工具
    result = mcp_call("excel-parser", "get_excel_column_info", {
        "excel_name": table_name
    })
    return result
```

### 3. 技能自带脚本

**analyzer.py 功能**：

| 功能 | 方法 | 说明 |
|------|------|------|
| 扫描配表 | scan_directory() | 收集所有配表文件 |
| 分析关系 | analyze_relations() | 分析表引用关系 |
| 提取约束 | extract_constraints() | 提取约束规则 |
| 生成图表 | generate_mermaid_graph() | 生成关系图 |

---

## 检测方法

### 项目工具检测

```python
def _check_project_tool(self) -> Dict:
    """检查项目特定工具"""
    # 1. 检查配置文件
    config_files = [
        ".gameconfig.yaml",
        ".gameconfig.yml",
        ".gameconfig.json",
        "pyproject.toml",
        "package.json"
    ]

    for config_file in config_files:
        config_path = self.project_dir / config_file
        if config_path.exists():
            return self._parse_config_file(config_path)

    # 2. 检查 scripts 目录
    scripts_dir = self.project_dir / "scripts"
    if scripts_dir.exists():
        return self._detect_script_tools(scripts_dir)

    # 3. 检查 tools 目录
    tools_dir = self.project_dir / "tools"
    if tools_dir.exists():
        return self._detect_script_tools(tools_dir)

    return None
```

### MCP 服务检测

```python
def _check_mcp_tool(self) -> Dict:
    """检查本地 MCP 服务"""
    try:
        # 列出所有 MCP 服务器
        mcp_list = list_mcp_resources()

        # 检查配置相关的服务
        config_tools = []
        for server in mcp_list:
            server_name = server.get("name", "").lower()
            if any(kw in server_name for kw in ["excel", "config", "parser"]):
                config_tools.append(server)

        if config_tools:
            return {
                "type": "mcp",
                "servers": config_tools
            }
    except:
        pass

    return None
```

### 技能脚本检测

```python
def _get_builtin_tool(self) -> Dict:
    """获取技能自带工具"""
    # 获取技能脚本目录
    skill_dir = Path(__file__).parent.parent
    scripts_dir = skill_dir / "scripts"

    # 检查 analyzer.py
    analyzer = scripts_dir / "analyzer.py"
    if analyzer.exists():
        return {
            "type": "builtin",
            "command": "python",
            "args": [str(analyzer)],
            "working_dir": str(scripts_dir)
        }

    # 如果没有脚本，返回 openpyxl 直接模式
    return {
        "type": "builtin_direct",
        "library": "openpyxl",
        "description": "直接使用 openpyxl 读取 Excel"
    }
```

---

## 兼容性处理

### 工具调用封装

```python
class ToolInvoker:
    """工具调用封装"""

    def __init__(self, tool_info: Dict):
        self.tool_info = tool_info
        self.tool_type = tool_info.get("type")

    def query(self, action: str, params: Dict) -> Dict:
        """执行查询"""
        if self.tool_type == "project":
            return self._invoke_project_tool(action, params)
        elif self.tool_type == "mcp":
            return self._invoke_mcp_tool(action, params)
        elif self.tool_type == "builtin":
            return self._invoke_builtin_tool(action, params)
        else:
            raise ValueError(f"未知工具类型: {self.tool_type}")

    def _invoke_project_tool(self, action: str, params: Dict) -> Dict:
        """调用项目工具"""
        command = self.tool_info.get("command")
        args = self.tool_info.get("args", [])

        # 替换占位符
        replaced_args = []
        for arg in args:
            arg = arg.replace("{action}", action)
            arg = arg.replace("{table}", params.get("table", ""))
            replaced_args.append(arg)

        # 执行命令
        result = subprocess.run(
            [command] + replaced_args,
            capture_output=True,
            text=True
        )

        return json.loads(result.stdout)

    def _invoke_mcp_tool(self, action: str, params: Dict) -> Dict:
        """调用 MCP 工具"""
        servers = self.tool_info.get("servers", [])
        server_name = servers[0] if servers else "excel-parser"

        # 调用 MCP 服务
        return mcp_call(server_name, action, params)

    def _invoke_builtin_tool(self, action: str, params: Dict) -> Dict:
        """调用内置工具"""
        if action == "scan":
            return self._builtin_scan(params)
        elif action == "analyze":
            return self._builtin_analyze(params)
        elif action == "validate":
            return self._builtin_validate(params)
        else:
            raise ValueError(f"未知操作: {action}")
```

### 结果格式统一

```python
def normalize_result(raw_result: Any, tool_type: str) -> Dict:
    """统一不同工具的输出格式"""
    if tool_type == "mcp":
        return {
            "success": True,
            "data": raw_result,
            "source": "mcp"
        }
    elif tool_type == "project":
        return {
            "success": raw_result.get("success", True),
            "data": raw_result.get("data", raw_result),
            "source": "project"
        }
    elif tool_type == "builtin":
        return {
            "success": True,
            "data": raw_result,
            "source": "builtin"
        }
    else:
        return {
            "success": False,
            "error": f"未知工具类型: {tool_type}"
        }
```

---

## 使用示例

### 工具选择

```python
# 创建工具选择器
selector = ToolSelector(project_dir="/path/to/project")

# 选择工具
tool_info = selector.select_tool()

print(f"选择工具: {tool_info['type']}")
print(f"工具详情: {tool_info}")
```

### 工具调用

```python
# 创建工具调用器
invoker = ToolInvoker(tool_info)

# 执行查询
result = invoker.query("scan", {"dir": "/path/to/configs"})

# 检查结果
if result["success"]:
    data = result["data"]
    print(f"查询成功，来源: {result['source']}")
else:
    print(f"查询失败: {result.get('error')}")
```

### 工具切换

```python
# 强制使用特定工具
selector = ToolSelector()

# 强制使用 MCP
mcp_tool = selector._check_mcp_tool()
if mcp_tool:
    invoker = ToolInvoker(mcp_tool)

# 强制使用内置工具
builtin_tool = selector._get_builtin_tool()
invoker = ToolInvoker(builtin_tool)
```
