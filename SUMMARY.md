# 项目总结

## 📁 项目结构

```
opengrok-aosp-mcp/
├── README.md              # 完整文档（功能、安装、使用）
├── config.json            # 配置文件
├── config.example.json    # 配置模板
├── pyproject.toml         # Python 依赖
├── server.py              # MCP 服务器入口
├── install.sh             # 自动安装脚本
├── test_connection.py     # 测试 OpenGrok 连接
├── test_all.py            # 快速测试所有工具
├── demo.py                # 完整演示和说明
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── opengrok_client.py # OpenGrok API 客户端
│   ├── cache.py           # 查询缓存（24h TTL）
│   └── token_optimizer.py # Token 优化（路径缩写、片段截断）
└── tools/                 # 工具实现
    ├── __init__.py
    └── basic.py           # 5 个基础工具
```

## 🛠️ 10 个工具说明（Milestone 1 + 2 + 3）

### 基础搜索工具 (5)

| 工具 | 功能 | 必需参数 | 可选参数 |
|------|------|----------|----------|
| `search_definitions` | 查找符号定义 | symbol | project, path, file_type, limit |
| `search_references` | 查找符号引用 | symbol | project, path, file_type, limit |
| `search_full` | 全文搜索 | query | project, path, file_type, limit |
| `get_file_content` | 获取文件内容 | path | start_line, end_line |
| `list_projects` | 列出项目 | 无 | 无 |

### AIDL + Binder 工具 (2)

| 工具 | 功能 | 必需参数 | 可选参数 |
|------|------|----------|----------|
| `find_aidl_impl` | 分析 AIDL 接口 | interface_name | limit |
| `trace_binder_chain` | 追踪 Binder 调用链 | interface_name, method_name | limit |

### System Service + JNI 工具 (3)

| 工具 | 功能 | 必需参数 | 可选参数 |
|------|------|----------|----------|
| `analyze_system_service` | 分析系统服务 | service_name | limit |
| `find_jni_bridge` | 查找 JNI 桥接 | java_class | limit |
| `trace_permission` | 追踪权限检查 | permission | limit |

## 🎯 Kiro 调用示例

### 1. search_definitions
```
User: 查找 ActivityManagerService 的定义
Kiro: [调用 search_definitions("ActivityManagerService")]

User: 在 frameworks/base 中查找 PowerManager
Kiro: [调用 search_definitions("PowerManager", path="frameworks/base")]
```

### 2. search_references
```
User: 查找 startActivity 在哪里被调用
Kiro: [调用 search_references("startActivity")]

User: 查找 WakeLock 的所有使用
Kiro: [调用 search_references("WakeLock")]
```

### 3. search_full
```
User: 搜索包含 "Binder transaction" 的代码
Kiro: [调用 search_full("Binder transaction")]

User: 搜索 TODO 注释
Kiro: [调用 search_full("TODO:")]
```

### 4. get_file_content
```
User: 查看 ActivityManagerService.java 的前 100 行
Kiro: [调用 get_file_content("frameworks/base/.../ActivityManagerService.java", 1, 100)]
```

### 5. list_projects
```
User: 列出所有项目
Kiro: [调用 list_projects()]
```

### 6. find_aidl_impl
```
User: 分析 IActivityManager 接口
Kiro: [调用 find_aidl_impl("IActivityManager")]
```

### 7. trace_binder_chain
```
User: 追踪 IActivityManager.startActivity 的调用链
Kiro: [调用 trace_binder_chain("IActivityManager", "startActivity")]
```

### 8. analyze_system_service
```
User: 分析 PowerManagerService
Kiro: [调用 analyze_system_service("power")]
```

### 9. find_jni_bridge
```
User: 查找 android.os.Process 的 JNI 实现
Kiro: [调用 find_jni_bridge("android.os.Process")]
```

### 10. trace_permission
```
User: 追踪 CAMERA 权限检查
Kiro: [调用 trace_permission("android.permission.CAMERA")]
```

## 📊 返回格式

### 搜索类工具（1-3）
```json
[
  {
    "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
    "line": 123,
    "snippet": "public class ActivityManagerService extends IActivityManager.Stub",
    "url": "http://localhost:8080/xref/frameworks/base/.../ActivityManagerService.java#123"
  }
]
```

### get_file_content
```json
{
  "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
  "start_line": 1,
  "end_line": 100,
  "total_lines": 5234,
  "text": "1: package com.android.server.am;\n2: \n3: import android.app.ActivityManager;\n..."
}
```

### list_projects
```json
["frameworks", "system", "hardware", "packages"]
```

## ✅ 测试清单

- [x] 代码结构优化（移除冗余文件）
- [x] 文档整合（README 包含所有信息）
- [x] Cache None 处理（所有工具支持无缓存模式）
- [x] 错误处理（401 认证错误友好提示）
- [x] 测试脚本（test_all.py, demo.py）
- [x] 工具说明清晰（参数、返回格式、使用示例）

## 🚀 快速开始

```bash
# 1. 安装
./install.sh

# 2. 测试
uv run python demo.py

# 3. 配置 Kiro
# 编辑 ~/.kiro/settings/mcp.json，添加：
{
  "mcpServers": {
    "opengrok-aosp": {
      "command": "uv",
      "args": ["--directory", "/path/to/opengrok-aosp-mcp", "run", "python", "server.py"]
    }
  }
}

# 4. 使用
kiro-cli chat
/tools trust-all
查找 ActivityManagerService 的定义
```

## 📝 待开发功能

- [x] Milestone 1: 基础框架 + 5 个基础工具
- [x] Milestone 2: AIDL + Binder 分析工具
- [x] Milestone 3: System Service + JNI 工具
- [ ] Milestone 4-7: 其他 AOSP 专用工具
- [ ] Milestone 8: 智能分析工具

## 🔧 优化点

1. **Token 优化**
   - 路径缩写：`frameworks/base` → `f/b`
   - 代码片段限制 5 行
   - 默认返回 10 条结果

2. **缓存机制**
   - 24 小时 TTL
   - 支持禁用缓存
   - MD5 键生成

3. **错误处理**
   - 401 认证错误友好提示
   - 连接失败重试
   - 超时设置（30s）
