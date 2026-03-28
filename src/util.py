#!/usr/bin/python3
# -.- coding: utf-8 -.-
# -.- dependencies: Python 3.8+ -.-

"""
Salt2Type

A tool to assist in migrating an existing codebase from Script# to TypeScript.

MIT License

Copyright (c) 2023 Pangaea Information Technologies, Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
from xml.etree import ElementTree
from typing import List, Optional, TextIO, Set
from src.types import *


def clean_line(line: str) -> str:
    """
    Prepares the specified line for typescript.
    """
    # Handle generic static method calls
    line = re.sub(r"\b([A-Za-z0-9$_]+)\(([^\(\)]+)\)\.call\(null,\s+", lambda m: f"{m.group(1)}<{to_type(m.group(2))}>(", line)

    # Handle generic method calls
    line = re.sub(r"\b([A-Za-z0-9$_]+)\(([^\(\)]+)\)\.call\(", lambda m: f"{m.group(1)}<{to_type(m.group(2))}>(", line)

    return line


def to_body(curr_class: ClassDef, lines: List[str]) -> List[str]:
    """
    Returns the specified method body formatted for inclusion inside the class.
    """
    return [clean_line(line.replace(curr_class.var_id, curr_class.name)) for line in lines]


def re_find_index(pattern: str, lines: List[str], start: int) -> int:
    """
    Finds the index of the line that matches the regex pattern starting from the specified index.
    """
    i = start
    while i < len(lines):
        if re.match(pattern, lines[i]):
            return i

        i += 1

    raise Exception("Could not find match for '%s'" % pattern)


def to_text(node: Optional[ElementTree.Element]) -> str:
    """
    Extracts the text from the specified Element, discarding any tags.  Also removes leading and trailing whitespace.
    """
    if node is not None:
        return "".join(node.itertext()).strip()

    return ""


def add_props(curr_class: ClassDef, lines: List[str], prefix: str, ignlist: Set) -> None:
    """
    Adds the properties and methods specified in the given source to the
    specified class.  Uses the prefix to determine the current indentation
    level.
    """
    if len(lines) == 1 and lines[0] == "":
        return

    i = 0
    while i < len(lines):
        line = lines[i]

        if match := re.match(r"^%s(.*): function\((.*)\) \{$" % prefix, line):
            end_line = re_find_index(r"^%s},?$" % prefix, lines, i + 1)
            # Method

            params = []
            type_params = None
            if (inner := re.match(r"^%s\treturn function\((.*)\) \{$" % prefix, lines[i + 1])) and re.match(
                r"^%s\t\};$" % prefix, lines[end_line - 1]
            ):
                # generic
                body = lines[i + 2 : end_line - 1]
                for prop in inner.group(1).split(", "):
                    if prop:
                        params.append(PropDef(prop))
                type_params = match.group(2).split(", ")

            else:
                # non-generic
                body = lines[i + 1 : end_line]
                for prop in match.group(2).split(", "):
                    if prop:
                        params.append(PropDef(prop))

            if "%s.%s:%s" % (curr_class.namespace, curr_class.name, match.group(1)) not in ignlist:
                curr_class.methods.append(MethodDef(match.group(1), params, None, to_body(curr_class, body), None, None, None, type_params))
            i = end_line
        elif match := re.match(r"^%s(.*): (.*[^,]),?$" % prefix, line):
            # Property
            if "%s.%s:%s" % (curr_class.namespace, curr_class.name, match.group(1)) not in ignlist:
                curr_class.props.append(PropDef(match.group(1), match.group(2)))
        else:
            raise Exception("Unsupported inner class line: %s" % line)

        i += 1


def to_type(raw_type: str) -> str:
    """
    Converts the raw Doxygen type into a valid typescript type.
    """
    optional = "?" in raw_type
    raw_type = raw_type.replace("?", "").replace("@", "").strip()

    raw_type = re.sub(r"\bbool\b", "boolean", raw_type)
    raw_type = re.sub(r"\b(int|float|double|long|short|byte|uint)\b", "number", raw_type)
    raw_type = re.sub(r"\b(ss\.)?(IList|List|IEnumerable|ICollection)\b", "Array", raw_type)
    raw_type = re.sub(r"\b(ss\.)?JsDate\b", "Date", raw_type)
    raw_type = re.sub(r"\b(ss\.)?Int32\b", "number", raw_type)
    raw_type = re.sub(r"\bDateTime\b", "Date", raw_type)
    raw_type = re.sub(r"\bObject\b", "any", raw_type)
    raw_type = re.sub(r"\bjQueryObject\b", "JQuery", raw_type)
    raw_type = re.sub(r"\bjQueryEvent\b", "JQuery.Event", raw_type)
    raw_type = re.sub(r"\bjQueryEventHandler\b", "JQuery.EventHandler", raw_type)
    raw_type = re.sub(r"\bdynamic\b", "any", raw_type)
    raw_type = re.sub(r"\bDelegate\b", "Action<void>", raw_type)
    raw_type = re.sub(r"^delegate (.*)$", r"Action<\1>", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary\<", r"Record<", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary$", r"Record<string,any>", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary([^<])", r"Record<string,any>\1", raw_type)
    raw_type = re.sub(r"^(sealed override|override|params|readonly|new|this|abstract|const) ", "", raw_type)

    if raw_type in ("any", "unknown", "boolean", "string", "void"):
        return raw_type

    if raw_type.endswith("[])") or raw_type.startswith("Array<"):
        return raw_type

    if raw_type.startswith("Record<") or raw_type.startswith("TypeOption<"):
        return raw_type

    if raw_type in ("number", "Date") and not optional:
        return raw_type

    return "%s | undefined" % raw_type


def find_prop(items: List[PropDef], name: str) -> Optional[PropDef]:
    """
    Finds the specified property by name (if it exists in the specified list.
    """
    for item in items:
        if item.name.lower() == name.lower():
            return item
        if item.name == "$" + name[:1].lower() + name[1:]:
            return item
        if name == "$" + item.name[:1].lower() + item.name[1:]:
            return item
        if item.is_rest and re.match(r"^%s[1-9]$" % re.escape(name), item.name, re.IGNORECASE):
            return item
        if item.name.lower() == "$" + name.lower():
            return item
        if name.lower() == "$" + item.name.lower():
            return item

    return None


def find_method(items: List[MethodDef], name: str, args: int) -> Optional[MethodDef]:
    """
    Finds the specified method by name and number of arguments (if it exists in the specified list.
    """
    matches = [
        item
        for item in items
        if item.name.lower() == name.lower()
        or item.name == "$" + name[:1].lower() + name[1:]
        or item.name.startswith("$" + name[:1].lower() + name[1:] + "$")
        or re.match(r"^%s\$[1-9]$" % re.escape(name), item.name, re.IGNORECASE)
        or (name == "" and item.name.startswith("$ctor"))
    ]

    for item in matches:
        if len(item.params) == args:
            return item

    if matches:
        return matches[0]

    return None


def copy_file(in_file: str, out_file: str, asm_name: str, ns_name: str) -> None:
    """
    Copies the specified source file to the specified destination file and replacing template keyword with their correct values.

    @param in_file: The template file to read in
    @param out_file: The output file to create
    @param asm_name: The name to pass to "ss.initAssembly"
    @param ns_name: The namespace to export for external use
    """
    lines = []
    with open(in_file, "r") as fil:
        for line in fil:
            line = line.replace("{{FILENAME}}", "%s.js" % asm_name)
            line = line.replace("{{LIBNAME}}", ns_name)
            lines.append(line)

    with open(out_file, "w") as fil:
        for line in lines:
            fil.write(line)


def to_local_prop(name: str) -> str:
    """
    Converts a C# local property to a S# name
    """
    if name[:1] == name[:1].lower():
        return "$" + name

    return name[:1].lower() + name[1:]


def prop_to_string(prop: PropDef, always_def: Optional[bool] = False) -> str:
    """
    Generates a stringified version of the property for typescript
    """
    myval = prop.def_val
    if always_def and not myval:
        if not prop.typ:
            myval = "undefined"
        elif prop.typ == "boolean":
            myval = "false"
        elif prop.typ == "number":
            myval = "0"
        elif prop.typ == "Date":
            myval = "new Date(0)"
        elif prop.typ == "string":
            myval = '""'
        elif prop.typ.endswith("[]"):
            myval = "[]"
        elif prop.typ.startswith("Array<") and prop.typ.endswith(">"):
            myval = "[]"
        elif "undefined" not in prop.typ:
            myval = "{} as " + prop.typ
        else:
            myval = "undefined"

    if myval == "null":
        myval = "undefined"

    if myval == "undefined" and prop.typ == "string":
        myval = '""'

    defval = " = %s" % myval if myval else ""
    typstr = ": %s" % (prop.typ or "any") if not defval or prop.typ else ""
    prefix = "..." if prop.is_rest else ("static " if prop.is_static else "")
    return "%s%s%s%s" % (prefix, prop.name, typstr, defval)


def find_class(link: str, defs: List[ClassDef]) -> Optional[ClassDef]:
    """
    Finds the specified class by namespace-qualified class name, var_id or doc_id.
    """
    for item in defs:
        if link in (item.doc_id, item.var_id, "%s.%s" % (item.namespace, item.name)):
            return item

    return None


def write_imports(
    defs: List[ClassDef],
    out_file: TextIO,
    curr_dir: str,
    ignore_var_id: Optional[str] = None,
    ignore_name: Optional[str] = None,
    extra_imports: Optional[List[str]] = None,
) -> None:
    """Writes all imports to the specified output stream except the specified ignore item"""
    out_file.write("import Enumerable from 'linq';\n")

    go_up = re.sub(r"[^\/]+", "..", curr_dir) or "."
    donelist = []

    for item in defs:
        if item.var_id and item.var_id != ignore_var_id:
            out_file.write("import %s from '%s/%s/%s';\n" % (item.var_id, go_up, item.namespace.replace(".", "/"), item.name))
        if item.name not in donelist and item.name != ignore_name:
            out_file.write("import %s from '%s/%s/%s';\n" % (item.name, go_up, item.namespace.replace(".", "/"), item.name))
            donelist.append(item.name)

    out_file.write("import * as ss from '%s/ss';\n" % go_up)
    out_file.write("import { Action, Delegate, Func, TypeOption } from '%s/ss/delegates';\n" % go_up)

    if extra_imports:
        for extra in extra_imports:
            out_file.write("%s\n" % extra.replace("{MAINDIR}", go_up))


def fix_body_line(line: str) -> str:
    """
    Applies fixes to a body line of typescript code.
    """
    line = re.sub(r"\bnull\b", "undefined", line)
    line = re.sub(r"^(\s*var [A-Za-z0-9$_]+) = \[\];\s*$", lambda m: f"{m.group(1)}: any[] = [];", line)
    line = re.sub(r"^(\s*var [A-Za-z0-9$_]+) = \{\};\s*$", lambda m: f"{m.group(1)}: any = {{}};", line)
    line = re.sub(r"^(\s*var [A-Za-z0-9$_]+) = \$.extend\(\{\}, ", lambda m: f"{m.group(1)}: any = $.extend({{}}, ;", line)

    line = re.sub(r"\b(ss\.)?(IList|List|IEnumerable|ICollection)\b", "Array", line)
    line = re.sub(r"\b(ss\.)?JsDate\b", "Date", line)
    line = re.sub(r"\b(ss\.)?Int32\b", "number", line)

    return line
