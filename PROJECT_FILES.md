# 项目文件清单

## 📄 文档文件 (4)

- `README.md` - 完整项目文档（功能、安装、使用、示例）
- `SUMMARY.md` - 项目总结和快速参考
- `TEST_REPORT.md` - 测试报告
- `PROJECT_FILES.md` - 本文件清单

## ⚙️ 配置文件 (3)

- `config.json` - 运行时配置
- `config.example.json` - 配置模板
- `pyproject.toml` - Python 项目配置和依赖

## 🐍 Python 代码 (8)

### 入口和服务器
- `server.py` - MCP 服务器入口点

### 核心模块 (core/)
- `core/__init__.py` - 模块导出
- `core/opengrok_client.py` - OpenGrok REST API 客户端
- `core/cache.py` - 磁盘缓存（diskcache）
- `core/token_optimizer.py` - Token 优化（路径缩写、片段截断）

### 工具实现 (tools/)
- `tools/__init__.py` - 工具导出
- `tools/basic.py` - 5 个基础搜索工具

### 测试和演示
- `test_connection.py` - 测试 OpenGrok 连接
- `test_all.py` - 快速测试所有工具
- `demo.py` - 完整演示和使用说明

## 🔧 脚本文件 (1)

- `install.sh` - 自动安装脚本

## 📊 统计

- 总文件数: 16
- Python 代码: 8 个文件
- 文档: 4 个文件
- 配置: 3 个文件
- 脚本: 1 个文件

## 🗂️ 目录结构

```
opengrok-aosp-mcp/
├── README.md              # 主文档
├── SUMMARY.md             # 项目总结
├── TEST_REPORT.md         # 测试报告
├── PROJECT_FILES.md       # 本文件
├── config.json            # 配置
├── config.example.json    # 配置模板
├── pyproject.toml         # Python 配置
├── server.py              # MCP 入口
├── install.sh             # 安装脚本
├── test_connection.py     # 连接测试
├── test_all.py            # 工具测试
├── demo.py                # 完整演示
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── opengrok_client.py
│   ├── cache.py
│   └── token_optimizer.py
└── tools/                 # 工具实现
    ├── __init__.py
    └── basic.py
```

## 🚫 忽略的文件/目录

- `.venv/` - Python 虚拟环境
- `.cache/` - 查询缓存
- `__pycache__/` - Python 字节码
- `uv.lock` - uv 锁文件
