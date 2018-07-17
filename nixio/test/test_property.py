# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import unittest
import nixio as nix
from .tmp import TempDir


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("proptest")
        self.testfilename = os.path.join(self.tmpdir.path, "proptest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.section = self.file.create_section("test section",
                                                "recordingsession")
        self.prop = self.section.create_property("test property", 0)
        self.prop_s = self.section.create_property("test str", nix.DataType.String)
        self.other = self.section.create_property("other property", nix.DataType.Int64)

    def tearDown(self):
        del self.file.sections[self.section.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_property_eq(self):
        assert(self.prop == self.prop)
        assert(not self.prop == self.other)
        assert(self.prop is not None)

    def test_property_id(self):
        assert(self.prop.id is not None)

        oid = "4a6e8483-0a9a-464d-bdd9-b39818334bcd"
        aprop = self.section.create_property("assign id", 0, oid)
        assert (aprop.id == oid)

        nonid = "I am not a proper uuid"
        noprop = self.section.create_property("invalid id", 0, nonid)
        assert (noprop.id != nonid)

    def test_property_name(self):
        assert(self.prop.name is not None)

    def test_property_definition(self):
        assert(self.prop.definition is None)

        self.prop.definition = "definition"
        assert(self.prop.definition == "definition")

        self.prop.definition = None
        assert(self.prop.definition is None)
        self.prop.definition = None

    def test_property_uncertainty(self):
        assert(self.prop.uncertainty is None)

        self.prop.uncertainty = 5
        assert(self.prop.uncertainty == 5)

        self.prop.uncertainty = None
        assert(self.prop.uncertainty is None)
        self.prop.uncertainty = None

    def test_property_reference(self):
        assert(self.prop.reference is None)

        self.prop.reference = "reference"
        assert(self.prop.reference == "reference")

        self.prop.reference = None
        assert(self.prop.reference is None)
        self.prop.reference = None

    def test_property_dependency(self):
        assert(self.prop.dependency is None)

        self.prop.dependency = "dependency"
        assert(self.prop.dependency == "dependency")

        self.prop.dependency = None
        assert(self.prop.dependency is None)
        self.prop.dependency = None

    def test_property_dependency_value(self):
        assert(self.prop.dependency_value is None)

        self.prop.dependency_value = "dependency value"
        assert(self.prop.dependency_value == "dependency value")

        self.prop.dependency_value = None
        assert(self.prop.dependency_value is None)
        self.prop.dependency_value = None

    def test_property_value_origin(self):
        assert(self.prop.value_origin is None)

        self.prop.value_origin = "value origin"
        assert(self.prop.value_origin == "value origin")

        self.prop.value_origin = None
        assert(self.prop.value_origin is None)
        self.prop.value_origin = None

    def test_property_unit(self):
        assert(self.prop.unit is None)

        self.prop.unit = "s"
        assert(self.prop.unit == "s")

        self.prop.unit = None
        assert(self.prop.unit is None)
        self.prop.unit = None

        # empty string units
        self.prop.unit = ""
        assert(self.prop.unit is None)
        self.prop.unit = " "
        assert(self.prop.unit is None)

        # non-si units
        self.prop.unit = "deg"
        assert(self.prop.unit == "deg")
        self.prop.unit = "mV/30"
        assert(self.prop.unit == "mV/30")

    def test_property_values(self):
        self.prop.values = [10]

        assert (self.prop.data_type == nix.DataType.Int64)
        assert(len(self.prop.values) == 1)

        assert(self.prop.values[0] == 10)
        assert(10 in self.prop.values)
        assert(12 not in self.prop.values)
        assert(self.prop.values[0] != 42)

        self.prop.delete_values()
        assert(len(self.prop.values) == 0)

        self.prop_s.values = ["foo", "bar"]
        assert(self.prop_s.data_type == nix.DataType.String)
        assert(len(self.prop_s.values) == 2)

        assert(self.prop_s.values[0] == "foo")
        assert("foo" in self.prop_s.values)
        assert(self.prop_s.values[0] != "bla")
        assert("bla" not in self.prop_s.values)


"""
class TestValue(unittest.TestCase):

    def test_value_int(self):
        value = nix.Value(10)
        other = nix.Value(11)

        assert(value.data_type == nix.DataType.Int64)

        assert(value == value)
        assert(value == 10)

        assert(value != other)
        assert(value != 11)

        value.value = 20
        assert(value == nix.Value(20))
        assert(value == 20)
        assert(value.value == 20)

    def test_value_float(self):
        value = nix.Value(47.11)
        other = nix.Value(3.14)

        assert(value.data_type == nix.DataType.Double)

        assert(value == value)
        assert(value == 47.11)

        assert(value != other)
        assert(value != 3.14)

        value.value = 66.6
        assert(value == nix.Value(66.6))
        assert(value == 66.6)
        assert(value.value == 66.6)

    def test_value_bool(self):
        value = nix.Value(True)
        other = nix.Value(False)

        assert(value.data_type == nix.DataType.Bool)

        assert(value == value)
        assert(value != other)
        assert(value)

        value.value = False
        assert(value == other)

    def test_value_str(self):
        value = nix.Value("foo")
        other = nix.Value("bar")

        assert(value.data_type == nix.DataType.String)

        assert(value == value)
        assert(value == "foo")

        assert(value != other)
        assert(value != "bar")

        value.value = "wrtlbrmpft"
        assert(value == nix.Value("wrtlbrmpft"))
        assert(value == "wrtlbrmpft")
        assert(value.value == "wrtlbrmpft")

    def test_value_attrs(self):
        value = nix.Value(0)

        value.reference = "a"
        assert(value.reference == "a")

        value.filename = "b"
        assert(value.filename == "b")

        value.filename = "c"
        assert(value.filename == "c")

        value.checksum = "d"
        assert(value.checksum == "d")

        value.uncertainty = 0.5
        assert(value.uncertainty == 0.5)
"""
