# CSV 转福昕书签 XML 工具

**v1.0.0** · Windows 桌面程序

把一份三列的分级 CSV（`级别` / `标题` / `物理页码`）转成福昕 PDF 高级编辑器可导入的书签 XML。

---

## 为什么需要它

福昕 PDF 编辑器不支持直接编辑书签，只能通过**导入 XML** 批量添加。手工编写 XML 很麻烦——层级要靠嵌套表达、每个节点要带四个属性、特殊字符要转义，几十上百条书签几乎无法手写。

本工具把这件事拆成两步：先在表格软件（或交给 AI 模型识别 PDF 标题）里整理出一个简单的 CSV，再由程序生成格式完全正确的 XML。

## 下载使用

到 [Releases](https://github.com/upquark-dev/csvtopdfbkmk/releases/latest) 下载 `csvtopdfbkmk.exe`：

- 单文件绿色版，免安装、免依赖（不需要装 Python）
- 双击运行，无控制台窗口
- 仅支持 Windows

## 使用流程

**1. 准备 CSV**

整理 PDF 的各级标题与其物理页码，存为 CSV。可以点界面上的【导入文件样式】查看格式说明，并在弹窗中点【CSV样式下载】拿到一份可直接编辑的模板。

**2. 转成 XML**

点【浏览...】选择 CSV。校验通过后状态栏会显示「共 X 条书签，最大层级 Y」，并在【生成深度级别】区域列出 `1级 / 2级 / …` 单选按钮——选中哪一级，就只导出到该层级为止。确认后点【生成并导出XML文件】。

**3. 导入福昕**

打开目标 PDF → 左侧「标签 / 书签」面板 → 导入 → 选择刚生成的 XML。

> 生成深度可以按需选择：同一份 CSV 可以先导一个「只到章节」的两级 XML 用于快速浏览，再导一个完整版用于精确定位，两者互不影响。

## CSV 格式

第一行表头必须包含以下三列，**列名一字不差**（列的顺序不限，多余的列会被忽略）：

| 列名 | 类型 | 说明 |
| --- | --- | --- |
| `级别` | 正整数 | 从 1 开始，1 为最高级；决定书签的层级与嵌套关系 |
| `标题` | 文本 | 书签显示的文字，不能为空 |
| `物理页码` | 正整数 | **PDF 的物理页码**（第 1 页就是 1），不是书上印刷的目录页码 |

示例：

```csv
级别,标题,物理页码
1,第一部分 基础知识,15
2,第1章 起步,16
3,1.1 搭建编程环境,17
4,1.1.1 Python版本,17
2,第2章 变量和简单数据类型,30
1,第二部分 进阶,88
```

要求：

- **编码必须是 UTF-8**。用 Excel / WPS 另存时选「CSV UTF-8」而不是普通「CSV」，否则中文会乱码。
- **行序即书签顺序**，程序不做排序，请按文档先后排列。
- 标题中包含逗号时，需按 CSV 规范用双引号包裹，例如 `2,"带, 逗号的标题",13`。
- 级别应逐级递进或回退。跳级（如 `1 → 3`）不会报错，但该节点实际仍位于第 2 层，容易与预期不符。

常见报错与原因：

| 报错 | 原因 |
| --- | --- |
| `缺少必填字段: 物理页码` | 表头写成了「页码」「页数」等，或含全角字符 / 多余空格 |
| `第 N 行「级别」值无效: 一` | 级别填了中文数字、空白或非正整数 |
| `第 N 行「物理页码」为空` | 该行缺值（行号从 2 开始，与表格软件的行号一致） |
| `CSV 文件为空` / `CSV 中没有数据行` | 只有表头或文件为空 |

## 导出的 XML

文件名默认为 `原CSV文件名_N级.xml`，UTF-8 编码（不带 BOM），4 空格缩进。结构如下（真实输出）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<BOOKMARKS>
    <ITEM NAME="第一部分 基础知识" PAGE="15" FITETYPE="Fit" INDENT="0">
        <ITEM NAME="第1章 起步" PAGE="16" FITETYPE="Fit" INDENT="1">
            <ITEM NAME="1.1 搭建编程环境" PAGE="17" FITETYPE="Fit" INDENT="2">
                <ITEM NAME="1.1.1 Python版本" PAGE="17" FITETYPE="Fit" INDENT="3"/>
            </ITEM>
        </ITEM>
        <ITEM NAME="第2章 变量和简单数据类型" PAGE="30" FITETYPE="Fit" INDENT="1"/>
    </ITEM>
    <ITEM NAME="第二部分 进阶" PAGE="88" FITETYPE="Fit" INDENT="0"/>
</BOOKMARKS>
```

每个 `<ITEM>` 有四个属性：

| 属性 | 取值 |
| --- | --- |
| `NAME` | 书签显示文字（来自「标题」列） |
| `PAGE` | 跳转页码（来自「物理页码」列） |
| `FITETYPE` | 固定为 `Fit`，即跳转后整页适合窗口 |
| `INDENT` | `级别 − 1`，0 为顶级 |

层级关系由**嵌套结构**表达（子书签写在父 `<ITEM>` 内部），`INDENT` 是福昕导入所需的冗余标记。

同一份 CSV 可反复导出不同深度；只要目标 PDF 本身的页数与排版没变，XML 就一直可用，更换 PDF 版本则需要重做 CSV。

## 从源码运行

需要 Python 3 与 tkinter（Windows 官方安装包默认自带）：

```bash
pip install -r requirements.txt
python main.py
```

程序只用到标准库（`csv` / `xml` / `tkinter`）。仓库中的 `requirements.txt` 为历史遗留，未实际使用；打包时需要的是带 tkinter 的解释器。

## 打包 exe

```bash
python -m venv venv-build
venv-build/Scripts/python.exe -m pip install pyinstaller
venv-build/Scripts/python.exe -m PyInstaller --onefile --windowed --name csvtopdfbkmk ^
  --distpath dist --workpath build/work --specpath build ^
  --version-file build/version_info.txt --noconfirm main.py
```

说明：必须使用**带 tkinter 的解释器**打包，否则生成的 exe 一启动就报错；`--specpath` 指向子目录时，务必给 `main.py` 等参数使用绝对路径。

## 项目结构

```
main.py              入口
src/__init__.py      版本号（唯一定义源）
src/converter.py     校验 CSV → 构建层级树 → 按深度截断 → 生成 XML
src/gui.py           Tkinter 界面
```

GUI 只在主线程操作控件：导出等耗时工作放在后台线程，结果通过 `window.after` 回主线程刷新界面。

## 版本记录

| 版本 | 说明 |
| --- | --- |
| v1.0.0 | 首个正式版本。CSV（`级别`/`标题`/`物理页码`）→ 福昕书签 XML；支持 1～N 级深度导出、CSV 样式模板下载、导入前校验与错误行号提示 |
