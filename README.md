# 权限管理系统 / Permission Management System

## 简介 / Introduction

**中文**

本系统是一个用于管理单位人员权限的桌面应用程序，主要实现对多个业务系统的人员权限进行统一管理。系统支持按人员、系统、权限级别进行多维度的权限分配和管理，提供直观的可视化操作界面。

**English**

This system is a desktop application for managing personnel permissions in organizations. It primarily implements unified management of personnel permissions across multiple business systems. The system supports multi-dimensional permission allocation and management by personnel, system, and permission level, providing an intuitive visual operation interface.

---

## 功能特性 / Features

### 主系统 / Main System

**中文**

- 人员信息管理（增删改查、导入导出、搜索刷新）
- 系统信息管理（多个业务系统）
- 权限信息管理（树形结构、导入导出、模板导出）
- 权限包管理（跨系统权限打包、分类管理、部分选中状态、详情树状展示）
- 人员-系统-权限关联管理
- 权限检查（展开权限包查看具体权限、当前权限/授权历史/权限汇总）
- 数据导入导出（YAML格式导出，支持基础权限信息和机构信息）
- 权限查询与统计
- 申请文件生成（Word文档）

**English**

- Personnel information management (CRUD, import/export, search and refresh)
- System information management (multiple business systems)
- Permission information management (tree structure, import/export, template export)
- Permission package management (cross-system permission packaging, category management, partial selection state, detailed tree view)
- Personnel-system-permission association management
- Permission check (expand permission packages to view specific permissions, current permissions/authorization history/permission summary)
- Data import/export (YAML format export, supporting basic permission information and organization information)
- Permission query and statistics
- Application file generation (Word documents)

### 子系统 / Sub System

**中文**

- 数据查看（权限信息、权限包、人员信息、授权记录）
- 授权检查（条式列表视图 + 树状视图，展开权限包查看具体权限）
- 申请文件生成（Word/YAML格式）
- 权限包申请
- 授权变更申请

**English**

- Data viewing (permission information, permission packages, personnel information, authorization records)
- Authorization check (list view + tree view, expand permission packages to view specific permissions)
- Application file generation (Word/YAML format)
- Permission package application
- Authorization change application

---

## 技术栈 / Tech Stack

| 类别 / Category | 技术 / Technology | 说明 / Description |
|----------------|-------------------|-------------------|
| 编程语言 / Programming Language | Python 3.8+ | 主要开发语言 / Main development language |
| GUI框架 / GUI Framework | tkinter | Python内置GUI库，跨平台 / Python built-in GUI library, cross-platform |
| 数据存储 / Data Storage | JSON + Parquet | JSON存储配置，Parquet存储业务数据 / JSON for configuration, Parquet for business data |
| 数据处理 / Data Processing | pandas | 处理Parquet文件及数据分析 / Process Parquet files and data analysis |
| 文档生成 / Document Generation | python-docx | 生成Word格式申请文件 / Generate Word format application files |
| 打包工具 / Packaging Tool | PyInstaller | 打包为可执行文件 / Package as executable files |

---

## 安装 / Installation

### 环境要求 / Requirements

- Python 3.8 或更高版本 / Python 3.8 or higher
- 操作系统 / Operating System: Windows 10/11

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 运行主系统 / Run Main System

```bash
python main.py
```

### 运行子系统 / Run Sub System

```bash
cd 子系统
python main.py
```

---

## 封装版 EXE 文件 / Packaged Executables

**中文**

本项目提供封装版可执行文件，可直接运行无需安装Python环境。请通过以下SHA-256哈希值验证文件完整性：

**English**

This project provides packaged executable files that can be run directly without installing Python environment. Please verify file integrity using the following SHA-256 hash values:

### 主系统封装版 / Main System Executable

```
SHA-256: 44702214AFC34C05E065442FF0B2A0524FDE8668242633F811A735AF87E66EF3
```

### 子系统封装版 / Sub System Executable

```
SHA-256: 27161DAD20AC973F43D36030791FE929E2F4A9E65979DDB263A67CE9E4FA05C4
```

### 验证方法 / Verification Method

**Windows (PowerShell):**
```powershell
Get-FileHash -Algorithm SHA256 <文件路径>
```

**Windows (命令提示符):**
```cmd
certutil -hashfile <文件路径> SHA256
```

---

## 项目结构 / Project Structure

```
quanXianGuanLi/
├── main.py                 # 主系统程序入口 / Main system entry
├── main.spec               # PyInstaller配置 / PyInstaller configuration
├── requirements.txt        # 依赖清单 / Dependencies list
├── pic.ico                 # 应用图标 / Application icon
├── app/                    # 主系统应用模块 / Main system application modules
│   ├── main_window.py      # 主窗口 / Main window
│   ├── pages/              # 页面模块 / Page modules
│   │   ├── home_page.py        # 首页 / Home page
│   │   ├── personnel_page.py   # 人员管理 / Personnel management
│   │   ├── system_page.py      # 系统管理 / System management
│   │   ├── permission_info_page.py  # 权限信息管理 / Permission info management
│   │   ├── permission_package_page.py  # 权限包管理 / Permission package management
│   │   ├── permission_assign_page.py  # 权限分配 / Permission assignment
│   │   ├── permission_check_page.py   # 权限检查 / Permission check
│   │   ├── statistics_page.py  # 统计查询 / Statistics and query
│   │   ├── import_export_page.py  # 导入与导出 / Import and export
│   │   └── settings_page.py    # 系统设置 / System settings
│   └── utils/              # 工具模块 / Utility modules
│       ├── config_manager.py  # 配置管理 / Configuration management
│       ├── data_manager.py    # 数据管理 / Data management
│       ├── path_utils.py      # 路径工具 / Path utilities
│       ├── import_export.py   # 导入导出工具 / Import/export utilities
│       └── logger.py          # 日志工具 / Logger utilities
├── 子系统/                  # 子系统目录 / Sub system directory
│   ├── main.py             # 子系统程序入口 / Sub system entry
│   ├── data_reader.py      # 数据读取模块 / Data reader module
│   ├── application_manager.py  # 申请管理模块 / Application manager module
│   └── storage_manager.py  # 缓存管理模块 / Storage manager module
└── templates/              # 模板目录 / Templates directory
    └── permission_template.csv  # 权限导入模板 / Permission import template
```

---

## 数据存储 / Data Storage

### 主系统存储目录 / Main System Storage Directory

```
[系统盘]/权限管理系统/              # 应用根目录 / Application root directory
├── config.json                    # 系统配置文件 / System configuration file
├── data/                          # 数据目录 / Data directory
│   ├── personnel.parquet          # 人员信息表 / Personnel table
│   ├── systems.parquet            # 系统信息表 / Systems table
│   ├── permissions.parquet        # 权限信息表 / Permissions table
│   ├── permission_assignments.parquet  # 权限分配表 / Permission assignments table
│   └── permission_packages.parquet     # 权限包表 / Permission packages table
├── templates/                     # 模板目录 / Templates directory
├── exports/                       # 导出目录 / Export directory
└── logs/                          # 日志目录 / Logs directory
```

---

## 许可证 / License

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 版本历史 / Version History

| 版本 / Version | 说明 / Description |
|---------------|-------------------|
| v1.0.0 | 初始版本发布 / Initial release |
| v1.1.0 | 新增权限包分类管理、权限树部分选中状态、权限检查页面 / Added permission package category management, partial selection state, permission check page |
| v1.2.0 | 新增人员管理搜索刷新功能、权限包详情树状展示、完善机构导出逻辑 / Added personnel search refresh, permission package detail tree view, improved organization export logic |
| v1.3.0 | 新增子系统授权检查双视图功能 / Added sub system authorization check dual view feature |
