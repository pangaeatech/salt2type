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

from dataclasses import dataclass
from typing import List, Optional


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
