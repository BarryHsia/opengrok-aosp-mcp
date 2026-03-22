# OpenGrok AOSP MCP Server

为 AOSP 开发设计的 MCP 服务器，通过 OpenGrok 提供智能代码导航和分析。

## 功能特性

### 16 个工具（完整实现）

#### 基础搜索工具 (5)

| 工具 | 功能 | 参数 |
|------|------|------|
| `search_definitions` | 查找符号定义 | symbol, project, path, file_type, limit |
| `search_references` | 查找符号引用 | symbol, project, path, file_type, limit |
| `search_full` | 全文搜索 | query, project, path, file_type, limit |
| `get_file_content` | 获取文件内容 | path, start_line, end_line |
| `list_projects` | 列出项目 | 无 |

#### AIDL + Binder 工具 (2)

| 工具 | 功能 | 参数 |
|------|------|------|
| `find_aidl_impl` | 分析 AIDL 接口 | interface_name, limit |
| `trace_binder_chain` | 追踪 Binder 调用链 | interface_name, method_name, limit |

#### System Service + JNI 工具 (3)

| 工具 | 功能 | 参数 |
|------|------|------|
| `analyze_system_service` | 分析系统服务 | service_name, limit |
| `find_jni_bridge` | 查找 JNI 桥接 | java_class, limit |
| `trace_permission` | 追踪权限检查 | permission, limit |

#### Advanced AOSP 工具 (6)

| 工具 | 功能 | 参数 |
|------|------|------|
| `find_hal_interface` | 查找 HAL 接口 | hal_name, hal_type, limit |
| `trace_broadcast` | 追踪广播流程 | action, limit |
| `search_selinux_policy` | 搜索 SELinux 策略 | query, limit |
| `find_resource_overlay` | 查找资源和 RRO | resource_name, limit |
| `trace_init_service` | 追踪 Init 服务 | service_name, limit |
| `analyze_build_module` | 分析构建模块 | module_name, limit |

### Token 优化

- 路径缩写：`frameworks/base` → `f/b`
- 代码片段限制 5 行
- 24 小时缓存
- 默认返回 10 条结果

## 快速开始

### 1. 安装

```bash
git clone <repo-url> opengrok-aosp-mcp
cd opengrok-aosp-mcp
./install.sh
```

### 2. 配置

编辑 `config.json`：

```json
{
  "opengrok": {
    "base_url": "http://localhost:8080",
    "token": null
  }
}
```

### 3. 测试

```bash
# 测试连接
uv run python test_connection.py

# 测试所有工具
uv run python test_all.py
```

### 4. 配置 Kiro CLI

编辑 `~/.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "opengrok-aosp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/opengrok-aosp-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### 5. 使用

```bash
kiro-cli chat

# 在 Kiro 中
/tools trust-all

# 测试工具
搜索 ActivityManagerService 的定义
查找 startActivity 的引用
```

## 工具使用示例

### 1. search_definitions - 查找符号定义

**用途**：查找函数、类、方法的定义位置

**参数**：
- `symbol` (必需): 符号名称，如 "ActivityManagerService"
- `project` (可选): 项目过滤
- `path` (可选): 路径过滤，如 "frameworks/base"
- `file_type` (可选): 文件类型，如 "java", "cpp"
- `limit` (可选): 最大结果数，默认 10

**示例**：
```
User: 查找 ActivityManagerService 的定义
Kiro: [调用 search_definitions("ActivityManagerService")]

User: 在 frameworks/base 中查找 PowerManager 的定义
Kiro: [调用 search_definitions("PowerManager", path="frameworks/base")]
```

**返回格式**：
```json
[
  {
    "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
    "line": 123,
    "snippet": "public class ActivityManagerService extends IActivityManager.Stub",
    "url": "http://localhost:8080/xref/frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java#123"
  }
]
```

### 2. search_references - 查找符号引用

**用途**：查找符号在哪些地方被使用

**参数**：同 search_definitions

**示例**：
```
User: 查找 startActivity 在哪里被调用
Kiro: [调用 search_references("startActivity")]

User: 查找 PowerManager.WakeLock 的所有使用
Kiro: [调用 search_references("WakeLock", path="frameworks")]
```

### 3. search_full - 全文搜索

**用途**：搜索包含特定文本的代码（支持正则表达式）

**参数**：
- `query` (必需): 搜索文本或正则表达式
- 其他参数同上

**示例**：
```
User: 搜索包含 "Binder transaction" 的代码
Kiro: [调用 search_full("Binder transaction")]

User: 搜索 TODO 注释
Kiro: [调用 search_full("TODO:")]
```

### 4. get_file_content - 获取文件内容

**用途**：读取指定文件的内容（带行号）

**参数**：
- `path` (必需): 文件路径
- `start_line` (可选): 起始行，默认 1
- `end_line` (可选): 结束行，默认 50

**示例**：
```
User: 查看 ActivityManagerService.java 的前 100 行
Kiro: [调用 get_file_content("frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java", start_line=1, end_line=100)]
```

**返回格式**：
```json
{
  "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
  "start_line": 1,
  "end_line": 100,
  "total_lines": 5234,
  "text": "1: package com.android.server.am;\n2: \n3: import android.app.ActivityManager;\n..."
}
```

### 5. list_projects - 列出项目

**用途**：列出 OpenGrok 中所有可用的项目

**参数**：无

**示例**：
```
User: 列出所有项目
Kiro: [调用 list_projects()]
```

### 6. find_aidl_impl - 分析 AIDL 接口

**用途**：分析 AIDL 接口的完整实现（接口定义、Stub、Proxy、服务注册）

**参数**：
- `interface_name` (必需): AIDL 接口名，如 "IActivityManager"
- `limit` (可选): 每个类型的最大结果数，默认 10

**示例**：
```
User: 分析 IActivityManager 接口
Kiro: [调用 find_aidl_impl("IActivityManager")]

User: 查看 IWindowManager 的实现
Kiro: [调用 find_aidl_impl("IWindowManager")]
```

**返回格式**：
```json
{
  "interface": {
    "path": "f/b/core/java/android/app/IActivityManager.aidl",
    "line": 1,
    "snippet": "interface IActivityManager {",
    "url": "http://localhost:8080/xref/..."
  },
  "stub": [
    {
      "path": "f/b/core/java/android/app/IActivityManager.java",
      "line": 123,
      "snippet": "public static abstract class Stub extends Binder",
      "url": "http://localhost:8080/xref/..."
    }
  ],
  "proxy": [...],
  "registration": [...]
}
```

### 7. trace_binder_chain - 追踪 Binder 调用链

**用途**：追踪 Binder IPC 调用链，从 Java 接口到 Native 实现

**参数**：
- `interface_name` (必需): 接口名，如 "IActivityManager"
- `method_name` (必需): 方法名，如 "startActivity"
- `limit` (可选): 每层的最大结果数，默认 10

**示例**：
```
User: 追踪 IActivityManager.startActivity 的调用链
Kiro: [调用 trace_binder_chain("IActivityManager", "startActivity")]

User: 查看 IWindowManager.addWindow 的实现路径
Kiro: [调用 trace_binder_chain("IWindowManager", "addWindow")]
```

**返回格式**：
```json
{
  "java_interface": [...],  // Java 接口定义
  "java_impl": [...],       // Java 实现（Stub）
  "jni_bridge": [...],      // JNI 桥接
  "native_impl": [...]      // Native 实现
}
```

### 8. analyze_system_service - 分析系统服务

**用途**：分析系统服务的完整生命周期（启动、注册、客户端使用）

**参数**：
- `service_name` (必需): 服务名，如 "activity", "power", "window"
- `limit` (可选): 每个类型的最大结果数，默认 10

**示例**：
```
User: 分析 ActivityManagerService
Kiro: [调用 analyze_system_service("activity")]

User: PowerManagerService 是如何启动的？
Kiro: [调用 analyze_system_service("power")]
```

**返回格式**：
```json
{
  "service_class": [...],    // 服务类定义
  "registration": [...],     // 服务注册
  "startup": [...],          // 启动逻辑
  "client_usage": [...]      // 客户端使用
}
```

### 9. find_jni_bridge - 查找 JNI 桥接

**用途**：查找 Java 类的 Native 方法和 JNI 实现

**参数**：
- `java_class` (必需): Java 类全名，如 "android.os.Process"
- `limit` (可选): 每个类型的最大结果数，默认 10

**示例**：
```
User: android.os.Process 的 JNI 实现在哪里？
Kiro: [调用 find_jni_bridge("android.os.Process")]

User: 查找 Binder 的 native 方法
Kiro: [调用 find_jni_bridge("android.os.Binder")]
```

**返回格式**：
```json
{
  "java_native_methods": [...],  // Java 中的 native 方法声明
  "jni_registration": [...],     // JNI 方法注册
  "native_impl": [...]           // Native 实现
}
```

### 10. trace_permission - 追踪权限检查

**用途**：追踪权限的定义、检查点和强制执行

**参数**：
- `permission` (必需): 权限全名，如 "android.permission.CAMERA"
- `limit` (可选): 每个类型的最大结果数，默认 10

**示例**：
```
User: CAMERA 权限在哪里检查？
Kiro: [调用 trace_permission("android.permission.CAMERA")]

User: 追踪 WRITE_EXTERNAL_STORAGE 权限
Kiro: [调用 trace_permission("android.permission.WRITE_EXTERNAL_STORAGE")]
```

**返回格式**：
```json
{
  "permission_definition": [...],  // 权限定义
  "check_points": [...],           // 检查点
  "enforcement": [...]             // 强制执行
}
```

## 典型使用场景

### 场景 1：理解某个类的实现

```
User: ActivityManagerService 是如何实现的？

Kiro 会：
1. search_definitions("ActivityManagerService") - 找到定义
2. get_file_content(...) - 查看类的主要代码
3. search_references("ActivityManagerService") - 查看哪里使用了它
```

### 场景 2：追踪方法调用链

```
User: startActivity 方法的调用链是什么？

Kiro 会：
1. search_definitions("startActivity") - 找到定义
2. search_references("startActivity") - 找到所有调用点
3. 逐层追踪调用关系
```

### 场景 3：查找特定功能的实现

```
User: 权限检查是如何实现的？

Kiro 会：
1. search_full("checkPermission") - 全文搜索
2. search_definitions("checkPermission") - 找到具体实现
3. get_file_content(...) - 查看实现细节
```

### 场景 4：分析 AIDL 接口

```
User: IActivityManager 接口是如何实现的？

Kiro 会：
1. find_aidl_impl("IActivityManager") - 分析接口、Stub、Proxy
2. 查看服务注册点
3. 理解 Binder 通信机制
```

### 场景 5：追踪 Binder 调用链

```
User: startActivity 是如何通过 Binder 调用的？

Kiro 会：
1. trace_binder_chain("IActivityManager", "startActivity")
2. 展示 Java → JNI → Native 的完整调用路径
3. 帮助理解跨进程通信流程
```

### 场景 6：分析系统服务

```
User: PowerManagerService 是如何工作的？

Kiro 会：
1. analyze_system_service("power")
2. 查看服务启动、注册和客户端使用
3. 理解系统服务架构
```

### 场景 7：查找 JNI 实现

```
User: android.os.Process 的 native 方法在哪里实现？

Kiro 会：
1. find_jni_bridge("android.os.Process")
2. 展示 Java native 声明和 C++ 实现
3. 理解 Java-Native 交互
```

### 场景 8：追踪权限检查

```
User: CAMERA 权限在哪里被检查？

Kiro 会：
1. trace_permission("android.permission.CAMERA")
2. 找到权限定义、检查点和强制执行
3. 理解权限机制
```

## 项目结构

```
opengrok-aosp-mcp/
├── README.md              # 本文件
├── config.json            # 配置文件
├── server.py              # MCP 服务器入口
├── install.sh             # 安装脚本
├── test_all.py            # 测试所有工具
├── test_connection.py     # 测试 OpenGrok 连接
├── core/
│   ├── opengrok_client.py # OpenGrok API 客户端
│   ├── cache.py           # 查询缓存
│   └── token_optimizer.py # Token 优化
└── tools/
    └── basic.py           # 5 个基础工具实现
```

## 故障排查

### OpenGrok 连接失败

```bash
# 测试连接
curl http://localhost:8080/api/v1/search?full=test&maxresults=1

# 检查 OpenGrok 是否运行
ps aux | grep opengrok
```

### 搜索结果为空

- 确认 OpenGrok 已索引源码
- 检查搜索的符号是否存在
- 尝试使用 `search_full` 进行全文搜索

### 认证错误 (401)

- 在 `config.json` 中配置 `token`
- 或在 OpenGrok 中禁用认证

## 开发路线

- [x] Milestone 1: 基础框架 + 5 个基础工具
- [x] Milestone 2: AIDL + Binder 分析工具
- [x] Milestone 3: System Service + JNI 工具
- [x] Milestone 4-7: Advanced AOSP 工具（HAL、Broadcast、SELinux、Resource、Init、Build）
- [ ] Milestone 8: 智能分析工具（可选）

**项目已完成核心功能，共 16 个工具！**

## 许可证

Apache 2.0

## 致谢

- 基于 [opengrok-mcp](https://github.com/SleepyDog053/opengrok-mcp)
- 使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架
- 为 [Kiro CLI](https://kiro.dev) 设计
