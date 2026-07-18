import csv
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

REQUIRED_FIELDS = {"级别", "标题", "页码"}


class ValidationError(Exception):
    pass


class BookmarkNode:
    def __init__(self, title, page, level):
        self.title = title
        self.page = page
        self.level = level
        self.children = []


def validate_csv(csv_path):
    if not os.path.isfile(csv_path):
        raise ValidationError(f"文件不存在: {csv_path}")
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValidationError("CSV 文件为空")
            headers = set(reader.fieldnames)
            missing = REQUIRED_FIELDS - headers
            if missing:
                raise ValidationError(f"缺少必填字段: {', '.join(sorted(missing))}")
            rows = list(reader)
            if not rows:
                raise ValidationError("CSV 中没有数据行")
            for i, row in enumerate(rows, start=2):
                level_val = row.get("级别", "").strip()
                title_val = row.get("标题", "").strip()
                page_val = row.get("页码", "").strip()
                if not level_val:
                    raise ValidationError(f"第 {i} 行「级别」为空")
                if not title_val:
                    raise ValidationError(f"第 {i} 行「标题」为空")
                if not page_val:
                    raise ValidationError(f"第 {i} 行「页码」为空")
                try:
                    level_num = int(level_val)
                    if level_num < 1:
                        raise ValueError
                except ValueError:
                    raise ValidationError(f"第 {i} 行「级别」值无效: {level_val}")
                try:
                    page_num = int(page_val)
                    if page_num < 1:
                        raise ValueError
                except ValueError:
                    raise ValidationError(f"第 {i} 行「页码」值无效: {page_val}")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"读取文件失败: {e}")
    return rows


def build_bookmark_tree(rows):
    if not rows:
        return []
    roots = []
    stack = []
    for row in rows:
        level = int(row["级别"])
        title = row["标题"].strip()
        page = int(row["页码"])
        node = BookmarkNode(title, page, level)
        while stack and stack[-1].level >= level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def truncate_tree(nodes, max_depth):
    indent = nodes[0].level - 1 if nodes else 0
    if indent >= max_depth:
        return []
    result = []
    for node in nodes:
        truncated = BookmarkNode(node.title, node.page, node.level)
        truncated.children = truncate_tree(node.children, max_depth)
        result.append(truncated)
    return result


def build_xml(nodes):
    root = Element("BOOKMARKS")
    for node in nodes:
        indent = node.level - 1
        el = Element("ITEM", attrib={
            "NAME": node.title,
            "PAGE": str(node.page),
            "FITETYPE": "Fit",
            "INDENT": str(indent),
        })
        _populate_children(el, node.children)
        root.append(el)
    xml_str = minidom.parseString(tostring(root, encoding="UTF-8")).toprettyxml(
        indent="    ", encoding="UTF-8"
    )
    return xml_str.decode("UTF-8")


def _populate_children(parent_el, children):
    for child in children:
        indent = child.level - 1
        el = SubElement(parent_el, "ITEM", attrib={
            "NAME": child.title,
            "PAGE": str(child.page),
            "FITETYPE": "Fit",
            "INDENT": str(indent),
        })
        _populate_children(el, child.children)


def csv_to_bookmark_xml(csv_path, xml_path, rows=4):
    rows_data = validate_csv(csv_path)
    tree = build_bookmark_tree(rows_data)
    tree = truncate_tree(tree, rows)
    xml_content = build_xml(tree)
    with open(xml_path, "w", encoding="UTF-8") as f:
        f.write(xml_content)
    return xml_path
