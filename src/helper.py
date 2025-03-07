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

import os, re, sys
from xml.etree import ElementTree
from dataclasses import dataclass
from typing import List, Tuple, Optional, TextIO, Set

#############
### TYPES ###
#############


@dataclass
class PropDef:
    """The definition of a property"""

    name: str
    """ the name of the property.  the name will be parameterized if it is generic. """

    def_val: Optional[str] = None
    """ The default value of the property (if known/applicable) """

    typ: Optional[str] = None
    """ The type of the property (if known). """

    desc: Optional[str] = None
    """ The brief description of the property (if known). """

    is_rest: Optional[bool] = None
    """ Whether or not this is a rest parameter (None if unknown). """

    is_static: Optional[bool] = None
    """ Whether or not this property is static (None if unknown). """


@dataclass
class MethodDef:
    """The definition of a class method"""

    name: str
    """
    the name of the method (empty string if it is the constructor).
    the name will be parameterized if it is generic.
    the name will be prefixed by "operator " if it is implicit.
    the name will be "this[...]" if it is an indexer.
    """

    params: List[PropDef]
    """ The ordered parameters of the method """

    typ: Optional[str] = None
    """ The return type of the method (if known). """

    body: Optional[List[str]] = None
    """ The lines making up the body of the method (if known). """

    desc: Optional[str] = None
    """ The brief description of the method (if known). """

    protection: Optional[str] = None
    """ The protection level for the method (None if unknown). """

    is_static: Optional[bool] = None
    """ Whether or not this method is static (None if unknown). """

    type_params: Optional[List[str]] = None
    """ If the method is generic, then this contains the type arguments (None if unknown). """


@dataclass
class ClassDef:
    """The definition of a class"""

    namespace: str
    """ The dot-separated namespace that contains the class. """

    name: str
    """ The name of the class. """

    doc_id: Optional[str]
    """ The ID used to refer to this class in documentation (if known). """

    methods: List[MethodDef]
    """ All of the methods in the class. """

    props: List[PropDef]
    """ All of the properties in the class. """

    links: List[str]
    """ The external classes which this class references. This can be specified as a namespace-qualified class name, or as a doc_id. """

    var_id: Optional[str]
    """ The variable name used to refer to this class in Script# (if known). """

    base_class: Optional[str]
    """ The base class that this class extends (if known/applicable). """

    interfaces: List[str]
    """ The interfaces that this class extends (if known/applicable). """

    is_generic: int = 0
    """ If non-zero then the class is generic (0 if non-generic OR if unknown). """

    is_enum: Optional[bool] = None
    """ Whether or not this class should be treated as an enum (None if unknown). """

    is_abstract: Optional[bool] = None
    """ Whether or not this class is abstract (None if unknown). """


######################
### Helper Methods ###
######################


def read_js(filename: str, ignfile: Optional[str]) -> Tuple[str, List[ClassDef], List[str]]:
    """
    Reads in the Script# file specified by the given filename and returns its parsed contents.

    @param filename: The JS file to read from
    @param ignfile: The ignore file to read from (if applicable)
    @return: The name to pass to "ss.initAssembly" followed by all of the class definitions found in the file, followed by all of the global
        statements to execute.
    """
    if ignfile:
        with open(ignfile, "r") as fil:
            ignlist = {i.strip() for i in fil.read().splitlines()}
    else:
        ignlist = set()

    with open(filename, "r") as fil:
        lines = fil.read().splitlines()

    asm_name = ""
    classes = {}  # key = ssVarName, value = ClassDef
    globs = []

    curr_class: Optional[ClassDef] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if line in ("(function() {", "\ufeff(function() {", "\t'use strict';", "})();", "\tvar $asm = {};") or line.startswith("\tss.setMetadata("):
            pass

        elif match := re.match(r"^\tglobal\.(.*) = (.*);$", line):
            # single-line global assignments
            if match.group(1) not in ignlist and match.group(2) not in ignlist:
                globs.append(clean_line(line))

        elif re.match(r"^\tglobal\..*;$", line):
            # single-line global directives
            globs.append(clean_line(line))

        elif re.match(r"^\t(.*)\.\$ctor1\.prototype = \1\.prototype;$", line) or re.match(
            r"^\t(.*)\.\$ctor\d\.prototype = \1\.\$ctor\d\.prototype = .*\.prototype;$", line
        ):
            # ignore single-line constructor directives since we're doing inheritance using typescript now
            pass

        elif match := re.match(r"^\t(global|\$\.fn)\..*\{$", line):
            # multi-line global directives
            end_line = re_find_index(r"^\t\}", lines, i + 1)
            for inner in lines[i : end_line + 1]:
                globs.append(clean_line(inner))
            i = end_line

        elif match := re.match(r"^\tss\.initAssembly\(\$asm, '(.*)'\);$", line):
            # initAssembly
            asm_name = match.group(1)

        elif match := re.match(r"^\t\/{80}$", line):
            # Class separator
            curr_class = None

        elif match := re.match(r"^\t\/\/ (.*)$", line):
            # Class name
            [namespace, name] = match.group(1).rsplit(".", 1)
            curr_class = ClassDef(namespace, name, None, [], [], [], None, None, [], 0)

        elif curr_class and (match := re.match(r"^\tvar (.*) = function\((.*)\) \{$", line)):
            # Class constructor
            var_id = match.group(1)
            curr_class.var_id = var_id
            if "%s.%s" % (curr_class.namespace, curr_class.name) not in ignlist:
                classes[var_id] = curr_class
            else:
                ignlist.add(var_id)

            params = []
            for prop in match.group(2).split(", "):
                if prop:
                    params.append(PropDef(prop))

            end_line = re_find_index(r"^\t\};$", lines, i + 1)
            curr_class.methods.append(MethodDef("", params, None, to_body(curr_class, lines[i + 1 : end_line])))
            i = end_line

        elif (
            curr_class
            and curr_class.var_id
            and (match := re.match(r"^\t%s\.([A-Za-z0-9$_]+) = function\((.*)\) \{$" % re.escape(curr_class.var_id), line))
        ):
            end_line = re_find_index(r"^\t\};$", lines, i + 1)
            # static class method

            params = []
            type_params = None
            if (inner := re.match(r"^\t\treturn function\((.*)\) \{$", lines[i + 1])) and re.match(r"^\t\t\};$", lines[end_line - 1]):
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
                curr_class.methods.append(MethodDef(match.group(1), params, None, to_body(curr_class, body), None, None, True, type_params))

            i = end_line

        elif curr_class and curr_class.var_id and (match := re.match(r"^\t%s\.([A-Za-z0-9$_]+) = (.*);$" % re.escape(curr_class.var_id), line)):
            # static class property
            if "%s.%s:%s" % (curr_class.namespace, curr_class.name, match.group(1)) not in ignlist:
                curr_class.props.append(PropDef(match.group(1), match.group(2), None, None, None, True))

        elif match := re.match(r"^\tss\.initClass\((.*), \$asm, \{$", line):
            # Class multi-line definition
            tmp_class = classes.get(match.group(1))
            end_line = re_find_index(r"^\t\}", lines, i + 1)

            if tmp_class:
                add_props(tmp_class, lines[i + 1 : end_line], r"\t\t", ignlist)

                final = lines[end_line]
                if final == "\t});":
                    pass
                elif inner := re.match(r"^\t\}, ([^, ]+)\);$", final):
                    tmp_class.base_class = inner.group(1)
                elif inner := re.match(r"^\t\}, null, \[(.*)\]\);$", final):
                    tmp_class.interfaces.extend(inner.group(1).split(", "))
                elif inner := re.match(r"^\t\}, ([^, ]+), \[(.*)\]\);$", final):
                    tmp_class.base_class = inner.group(1)
                    tmp_class.interfaces.extend(inner.group(2).split(", "))
                else:
                    raise Exception("Unsupported initClass multi-line ending: %s" % final)

            i = end_line

        elif match := re.match(r"^\tss\.initClass\((.*), \$asm, \{(.*)\}(.*)\);$", line):
            # Class single-line definition
            tmp_class = classes.get(match.group(1))

            if tmp_class:
                add_props(tmp_class, match.group(2).strip().split(", "), r"", ignlist)

                final = match.group(3)
                if final == "":
                    pass
                elif inner := re.match(r"^, ([^, ]+)$", final):
                    tmp_class.base_class = inner.group(1)
                elif inner := re.match(r"^, null, \[(.*)\]$", final):
                    tmp_class.interfaces.extend(inner.group(1).split(", "))
                elif inner := re.match(r"^, ([^, ]+), \[(.*)\]$", final):
                    tmp_class.base_class = inner.group(1)
                    tmp_class.interfaces.extend(inner.group(2).split(", "))
                else:
                    raise Exception("Unsupported initClass single-line ending: %s" % final)

        elif match := re.match(r"^\tss\.initInterface\((.*), \$asm, \{(.*)\}(.*)\);$", line):
            # Interface definition
            tmp_class = classes.get(match.group(1))

            if tmp_class:
                add_props(tmp_class, match.group(2).strip().split(", "), r"", ignlist)

                final = match.group(3)
                if final == "":
                    pass
                elif inner := re.match(r"^, \[(.*)\]$", final):
                    tmp_class.interfaces.extend(inner.group(1).split(", "))
                else:
                    raise Exception("Unsupported initInterface ending: %s" % final)

        elif match := re.match(r"^\tss\.initGeneric(Class|Interface)\((.*), \$asm, ([1-9][0-9]*)\);$", line):
            # Generic definition
            tmp_class = classes.get(match.group(2))
            if tmp_class:
                tmp_class.is_generic = int(match.group(3))

        elif match := re.match(r"^\tss\.initEnum\((.*), \$asm, \{(.*)\}(, true)?\);$", line):
            # Enum definition
            tmp_class = classes.get(match.group(1))
            if tmp_class:
                add_props(tmp_class, match.group(2).strip().split(", "), r"", ignlist)
                tmp_class.is_enum = True

        elif line == "\t(function() {":
            # multi-line initialization functions
            globs.append("")
            end_line = re_find_index(r"^\t\}\)\(\);", lines, i + 1)
            inits = lines[i + 1 : end_line]

            for init in inits:
                if match := re.match(r"^\t\t([A-Za-z0-9$_]+)\.([A-Za-z0-9$_]+) = (\[[^\[]*\]|\"[^\"]*\"|'[^']*'|\{[^\}]*\}|[0-9.-]+|null);$", init):
                    tmp_class = classes.get(match.group(1))
                    if tmp_class:
                        tmp_class.props.append(PropDef(match.group(2), match.group(3), None, None, None, True))
                    elif match.group(1) not in ignlist:
                        globs.append(clean_line(init))
                elif match := re.match(r"^\t\t([A-Za-z0-9$_]+)\.([A-Za-z0-9$_]+) = ", init):
                    tmp_class = classes.get(match.group(1))
                    if tmp_class:
                        tmp_class.props.append(PropDef(match.group(2), None, None, None, None, True))

                    if match.group(1) not in ignlist:
                        globs.append(clean_line(init))
                elif match := re.match(r"^\t\t([A-Za-z0-9$_]+)\.", init):
                    if match.group(1) not in ignlist:
                        globs.append(clean_line(init))
                else:
                    globs.append(clean_line(init))

            i = end_line

        else:
            raise Exception("Unsupported line: %s" % line)

        i += 1

    return asm_name, classes.values(), globs


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
    raw_type = re.sub(r"\bDateTime\b", "Date", raw_type)
    raw_type = re.sub(r"\bObject\b", "object", raw_type)
    raw_type = re.sub(r"\bjQueryObject\b", "JQuery", raw_type)
    raw_type = re.sub(r"\bjQueryEvent\b", "JQuery.Event", raw_type)
    raw_type = re.sub(r"\bjQueryEventHandler\b", "JQuery.EventHandler", raw_type)
    raw_type = re.sub(r"\bdynamic\b", "any", raw_type)
    raw_type = re.sub(r"\bDelegate\b", "Action<void>", raw_type)
    raw_type = re.sub(r"^delegate (.*)$", r"Action<\1>", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary\<", r"Record<", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary$", r"Record<string,unknown>", raw_type)
    raw_type = re.sub(r"(ss\.)?(Js)?Dictionary([^<])", r"Record<string,unknown>\1", raw_type)
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


def read_doc(filename: str) -> List[ClassDef]:
    """
    Reads in the XML Doxygen file specified by the given filename and returns its parsed contents.

    @param filename: The XML file to read from
    @return: All of the class definitions found in the file.
    """
    classes = {}  # key = `${namespace}.${name}`, value = ClassDef

    root = ElementTree.parse(filename).getroot()
    for compound in root.findall("compounddef"):
        kind = compound.get("kind")

        if kind in ("class", "interface"):
            key = compound.find("compoundname").text.replace("::", ".")
            [namespace, name] = key.rsplit(".", 1)
            doc_id = compound.get("id")
            is_abstract = compound.get("abstract") == "yes"
            methods = []
            props = []
            links = []

            classes[key] = ClassDef(namespace, name, doc_id, methods, props, links, None, None, [], 0, None, is_abstract)

            for member in compound.findall("./sectiondef/memberdef"):
                kind = member.get("kind")
                prot = member.get("prot")
                is_static = member.get("static") == "yes"
                mname = member.find("name").text
                if "<" in mname:
                    mname = re.sub(r" *<.*>", "", mname)
                desc = to_text(member.find("briefdescription"))
                type_node = member.find("type")
                for ref in type_node.findall("ref"):
                    links.append(ref.get("refid"))
                typ = to_type(to_text(type_node))
                if not typ and mname == name:
                    typ = name

                if kind in ("property", "variable", "event"):
                    props.append(PropDef(mname, None, typ, desc))
                    methods.append(MethodDef("get_%s" % mname, [], typ, None, desc, prot, is_static))
                    methods.append(MethodDef("get_$%s" % mname, [], typ, None, desc, prot, is_static))
                    methods.append(MethodDef("set_%s" % mname, [PropDef("value", None, typ)], "void", None, desc, prot, is_static))
                    methods.append(MethodDef("set_$%s" % mname, [PropDef("value", None, typ)], "void", None, desc, prot, is_static))

                elif kind == "function":
                    params = []
                    for param in member.findall("param"):
                        pname = param.find("declname").text
                        ptype_node = param.find("type")
                        for ref in ptype_node.findall("ref"):
                            links.append(ref.get("refid"))
                        ptyp = to_type(to_text(ptype_node))
                        prest = to_text(ptype_node).startswith("params ")
                        params.append(PropDef(pname, None, ptyp, None, prest))

                    methods.append(MethodDef(mname if mname != name else "", params, typ, None, desc, prot, is_static))

    return classes.values()


def find_prop(items: List[PropDef], name: str) -> Optional[PropDef]:
    """
    Finds the specified property by name (if it exists in the specified list.
    """
    for item in items:
        if item.name.lower() == name.lower():
            return item
        if item.is_rest and re.match(r"^%s[1-9]$" % re.escape(name), item.name, re.IGNORECASE):
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


def add_doc_info(defs: List[ClassDef], types: List[ClassDef]) -> None:
    """
    Updates the class definitions found in C{defs} to specify all of the documentation details found in C{types}.

    @param defs: The class definitions (from JS) to modify in-place to add type definitions.
    @param types: The type definitions (from XML) to use for lookup.
    """
    classes = {}  # key = `${namespace}.${name}`, value = ClassDef
    for curr_class in defs:
        key = "%s.%s" % (curr_class.namespace, curr_class.name)
        classes[key] = curr_class

    for typ in types:
        key = "%s.%s" % (typ.namespace, typ.name)
        curr_class = classes.get(key)

        if curr_class:
            curr_class.doc_id = typ.doc_id
            curr_class.is_abstract = typ.is_abstract

            for method in typ.methods:
                curr_method = find_method(curr_class.methods, method.name, len(method.params))

                if curr_method:
                    curr_method.typ = method.typ
                    curr_method.desc = method.desc
                    curr_method.protection = method.protection
                    curr_method.is_static = curr_method.is_static or method.is_static

                    for param in method.params:
                        curr_param = find_prop(curr_method.params, param.name)

                        if curr_param:
                            curr_param.typ = param.typ
                            curr_param.desc = param.desc
                            curr_param.is_rest = param.is_rest

            for prop in typ.props:
                curr_prop = find_prop(curr_class.props, prop.name)

                if curr_prop:
                    curr_prop.typ = prop.typ
                    curr_prop.desc = prop.desc
                    curr_prop.is_rest = prop.is_rest
                elif not prop.name.startswith("this["):
                    curr_class.props.append(PropDef(to_local_prop(prop.name), None, prop.typ, prop.desc, prop.is_rest, False))

            curr_class.links.extend(typ.links)


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


def copy_tpl(out_dir: str, asm_name: str, ns_name: str) -> None:
    """
    Copies the C{tpl} contents into the specified output directory (creating it first if it doesn't already exist) and replacing
    template keywords with their correct values.

    @param out_dir: The output directory
    @param asm_name: The name to pass to "ss.initAssembly"
    @param ns_name: The namespace to export for external use
    """
    tpl_dir = os.path.join(os.path.dirname(sys.argv[0]), "tpl")
    ignored_dirs = list(map(lambda f: os.path.join(tpl_dir, f), ("coverage", "dist", "node_modules")))

    def is_ignored(dir_name: str) -> bool:
        for ignored_dir in ignored_dirs:
            if dir_name.startswith(ignored_dir):
                return True
        return False

    for src_dir, _, files in os.walk(tpl_dir):
        if not is_ignored(src_dir):
            dst_dir = src_dir.replace(tpl_dir, out_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for fil in files:
                src_file = os.path.join(src_dir, fil)
                dst_file = os.path.join(dst_dir, fil)
                copy_file(src_file, dst_file, asm_name, ns_name)


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


def gen_ts(out_dir: str, defs: List[ClassDef], extra_imports: Optional[List[str]] = None) -> None:
    """
    Generates the typescript files for each known class in the specified output directory.

    @param out_dir: The output directory
    @param defs: The classes
    """
    for item in defs:
        dst_dir = os.path.join(out_dir, "src", item.namespace.replace(".", "/"))
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        with open(os.path.join(dst_dir, "%s.ts" % item.name), "w") as fil:
            write_imports(defs, fil, item.namespace.replace(".", "/"), item.var_id, item.name, extra_imports)
            fil.write("\n")

            if item.is_enum:
                fil.write("enum %s {\n" % item.name)
                for prop in item.props:
                    if not prop.name.startswith("__"):
                        fil.write("\n")
                        if prop.desc:
                            fil.write("\t/** %s **/\n" % prop.desc)
                        fil.write("\t%s%s,\n" % (prop.name, " = %s" % prop.def_val if prop.def_val else ""))

                fil.write("}\n")
                fil.write("\n")
                fil.write("export default %s\n" % item.name)
                continue

            if item.is_generic:
                fil.write("/** [Generic] **/\n")

            interfaces = "implements %s " % ", ".join(item.interfaces) if item.interfaces else ""
            baseclass = "extends %s " % item.base_class if item.base_class else ""
            fil.write("%sclass %s %s%s{\n" % ("abstract " if item.is_abstract else "", item.name, baseclass, interfaces))

            for prop in item.props:
                fil.write("\n")
                if prop.desc:
                    fil.write("\t/** %s **/\n" % prop.desc)
                fil.write("\t%s;\n" % prop_to_string(prop, True))

            for method in item.methods:
                fil.write("\n")
                if method.desc:
                    fil.write("\t/** %s **/\n" % method.desc)
                props = ", ".join(map(prop_to_string, method.params))
                prot = method.protection if method.protection in ("public", "private", "protected") else ""
                gen = ("<%s>" % ",".join(method.type_params)) if method.type_params else ""
                if method.name:
                    fil.write("\t%s %s%s%s(%s): %s {\n" % (prot, "static " if method.is_static else "", method.name, gen, props, method.typ or "any"))
                else:
                    fil.write("\tconstructor%s(%s) {\n" % (gen, props))
                for line in method.body:
                    fil.write("\t%s\n" % fix_body_line(line))
                fil.write("\t}\n")

            fil.write("}\n")

            fil.write("\n")
            fil.write("export default %s;" % item.name)


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

    return line


def gen_index(out_dir: str, defs: List[ClassDef], globs: List[str], extra_imports: Optional[List[str]] = None) -> None:
    """
    Generates the index.ts file exporting each known class in the specified output directory.

    @param out_dir: The output directory
    @param defs: The classes
    @param globs: The global method lines
    """
    with open(os.path.join(out_dir, "src", "index.ts"), "w") as fil:
        write_imports(defs, fil, "", "", "", extra_imports)

        fil.write("\n")
        for glob in globs:
            fil.write("%s\n" % fix_body_line(glob))
