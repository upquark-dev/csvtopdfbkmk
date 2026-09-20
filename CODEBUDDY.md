# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## 项目概述

CSV 转福昕书签 XML 工具：将人工/模型整理的分级书签 CSV 转换为福昕高级编辑器（Foxit PDF）可导入的 XML 格式。单机桌面工具，Python + Tkinter，无测试、无 lint 配置。

## 常用命令

```bash
# 安装依赖（仅声明 pandas，但当前代码实际只用标准库 csv/xml/tkinter）
pip install -r requirements.txt

# 运行 GUI 应用（入口）
python main.py
```

仓库中没有测试、lint 或构建脚本。`dist/csvtopdfbkmk.exe` 是预构建产物（推测由 PyInstaller 打包），仓库内无对应的 spec/构建配置——如需重新打包，需先与用户确认打包方式，不要凭空创建构建流程。

## 架构

三层结构，依赖方向单一（`main.py` → `gui.py` → `converter.py`）：

- **`main.py`** — 唯一入口，实例化 `src.gui.App` 并进入 mainloop。
- **`src/gui.py`（App 类）** — 全部 Tkinter UI 与交互逻辑：
  - 浏览选择 CSV 后立即调用 `validate_csv` 预校验；校验通过才根据数据中的最大层级动态重建"生成深度级别"单选按钮（`_rebuild_rows_buttons`）。
  - 导出在后台 `threading.Thread` 中执行（避免阻塞 UI），完成后通过 `self.window.after(0, ...)` 回到主线程弹窗。**修改 GUI 代码时必须维持这一线程约定：后台线程不得直接操作 Tkinter 控件。**
  - `last_valid_path` 用于确保导出的文件就是已通过校验的文件。
- **`src/converter.py`** — 核心转换逻辑，与 UI 完全解耦，是唯一需要单元测试价值的模块。处理管线：
  1. `validate_csv` — 校验并返回行数据。硬编码要求表头包含 `级别`、`标题`、`页码` 三列（`REQUIRED_FIELDS`），级别/页码必须为正整数；以 `utf-8-sig` 读取（兼容 Excel BOM）。失败抛 `ValidationError`（含中文行号定位信息），GUI 捕获它区分校验错误与其他异常。
  2. `build_bookmark_tree` — 用栈按 `级别` 构建多叉树（栈顶 level ≥ 当前 level 时出栈）。
  3. `truncate_tree` — 按 `rows` 参数截断深度（对应 GUI 上的"N级"选择）。
  4. `build_xml` — 生成 `<BOOKMARKS><ITEM NAME=... PAGE=... FITETYPE="Fit" INDENT=...>` 结构，`INDENT = 级别 - 1`，经 minidom 美化输出。**XML 属性名（NAME/PAGE/FITETYPE/INDENT）与缩进规则是福昕导入的格式契约，不可随意更改。**

## 注意事项

- 所有用户可见文案（状态栏、弹窗、异常消息）均为简体中文，UI 字体依赖"Microsoft YaHei"，这是 Windows 专用应用（`os.startfile` 仅 Windows 可用）。
- 页码语义是 PDF 物理页码（第 1 页 = 1），不是书签/目录页码。
- CSV 模板内容由 `gui._export_template` 中的 `FORMAT_INFO` 与硬编码示例字符串生成，修改格式规则时两处需同步。
