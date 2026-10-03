# CSV转福昕书签XML工具 v1.0.0

1. 先制作没有书签的pdf的书签，制作成csv格式（人工编辑或最好用模型识别pdf中的各级标题及物理页码做成分级书签并按csv格式要求保存，csv的样式在软件中下载）
2. 将csv格式的书签用本软件《csvtopdfbkmk》转换成福昕foxitpdf高级编辑器可以导入的xml格式
3. 用福昕foxitpdf高级编辑器标签中的导入功能导入xml格式的书签

## 运行

```
pip install -r requirements.txt
python main.py
```

## 版本

| 版本 | 说明 |
| --- | --- |
| v1.0.0 | 首个正式版本。CSV（`级别`/`标题`/`物理页码`）→ 福昕书签 XML；支持 1～N 级深度导出、CSV 样式模板下载、导入前校验与错误行号提示 |

版本号定义在 `src/__init__.py` 的 `__version__`，窗口标题与状态栏均引用该值，升级时只改这一处。
