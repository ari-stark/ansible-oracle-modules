import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oracle_tablespace import *


class TestSize(unittest.TestCase):
    def test_to_string_unlimited(self):
        size = Size('unlimited')
        self.assertEqual('unlimited', str(size))

    def test_to_string_int(self):
        size = Size(123)
        self.assertEqual('123.0', str(size))
        size = Size(125952)
        self.assertEqual('123.0K', str(size))

    def test_to_string_oracle_format(self):
        size = Size('15M')
        self.assertEqual('15.0M', str(size))
        size = Size('125952K')
        self.assertEqual('123.0M', str(size))
        size = Size('0.5M')
        self.assertEqual('512.0K', str(size))
        size = Size('1024E')
        self.assertEqual('1.0Z', str(size))

    def test_equals(self):
        self.assertEqual(Size('10M'), Size('10M'))
        self.assertNotEqual(Size('10M'), Size('20M'))
        self.assertNotEqual(Size('10M'), Size('unlimited'))
        self.assertEqual(Size('unlimited'), Size('unlimited'))
        self.assertNotEqual(Size('1M'), 'foo')

    def test_compare(self):
        size1 = Size('1M')
        size2 = Size('1.5M')
        self.assertGreater(size2, size1)
        self.assertLess(size1, size2)
        self.assertFalse(size1 < size1)
        self.assertFalse(size1 > size1)
        self.assertGreater(Size('unlimited'), size2)
        self.assertFalse(Size('unlimited') < size2)
        self.assertLess(size2, Size('unlimited'))
        self.assertFalse(size2 > Size('unlimited'))


class TestDataFile(unittest.TestCase):
    def test_constructor_with_default(self):
        d = Datafile('/path/to/dbf', '0.5K')
        self.assertEqual('/path/to/dbf', d.path)
        self.assertEqual(512, d.size.size)
        self.assertFalse(d.autoextend)
        self.assertIsNone(d.nextsize)
        self.assertIsNone(d.maxsize)

    def test_constructor_with_value(self):
        d = Datafile('/path/to/dbf', '0.5K', True, '1M', 'unlimited')
        self.assertEqual('/path/to/dbf', d.path)
        self.assertEqual('512.0', str(d.size))
        self.assertTrue(d.autoextend)
        self.assertEqual('1.0M', str(d.nextsize))
        self.assertEqual('unlimited', str(d.maxsize))

    def test_needs_resize(self):
        new = Datafile('/path/to/dbf', 1024, True)
        prev = Datafile('/path/to/dbf', 512)
        self.assertFalse(new.needs_resize(prev), 'no need to resize because of autoextend')

        new = Datafile('/path/to/dbf', 1024)
        prev = Datafile('/path/to/dbf', 512)
        self.assertTrue(new.needs_resize(prev), 'need to resize because new is bigger')

        new = Datafile('/path/to/dbf', 512)
        prev = Datafile('/path/to/dbf', 1024)
        self.assertFalse(new.needs_resize(prev), 'no resize because new is smaller')

    def test_needs_change_autoextend(self):
        new = Datafile('/path/to/dbf', 1024, True)
        prev = Datafile('/path/to/dbf', 512, False)
        self.assertTrue(new.needs_change_autoextend(prev), 'from autoextend off to autoextend on')

        new = Datafile('/path/to/dbf', 1024, False, '2M', '20M')
        prev = Datafile('/path/to/dbf', 512, False, '1M', '10M')
        self.assertFalse(new.needs_change_autoextend(prev), 'autoextend off, even if nextsize and maxsize change')

        new = Datafile('/path/to/dbf', 512, False)
        prev = Datafile('/path/to/dbf', 1024, True)
        self.assertTrue(new.needs_change_autoextend(prev), 'from autoextend on to autoextend off')

        new = Datafile('/path/to/dbf', 512, True, '1M', '20M')
        prev = Datafile('/path/to/dbf', 1024, True, '1M', '10M')
        self.assertTrue(new.needs_change_autoextend(prev), 'sizes change')

        new = Datafile('/path/to/dbf', 512, True, '1M', '20M')
        prev = Datafile('/path/to/dbf', 1024, True, '1M', '20M')
        self.assertFalse(new.needs_change_autoextend(prev), 'same values')

    def test_autoextend_clause(self):
        d = Datafile('/path/to/dbf', 512, False)
        self.assertEqual(' autoextend off', d.autoextend_clause())

        d = Datafile('/path/to/dbf', 1024, False, '2M', '20M')
        self.assertEqual(' autoextend off', d.autoextend_clause())

        d = Datafile('/path/to/dbf', 1024, True)
        self.assertEqual(' autoextend on', d.autoextend_clause())

        d = Datafile('/path/to/dbf', 512, True, '1M', '20M')
        self.assertEqual(' autoextend on next 1.0M maxsize 20.0M', d.autoextend_clause())

    def test_file_specification_clause(self):
        d = Datafile('/path/to/dbf', 512, False)
        self.assertEqual('size 512.0 reuse  autoextend off', d.file_specification_clause())

        d = Datafile('/path/to/dbf', 1024, True)
        self.assertEqual('size 1.0K reuse  autoextend on', d.file_specification_clause())

    def test_data_file_clause(self):
        d = Datafile('/path/to/dbf', 512, False)
        self.assertEqual("'/path/to/dbf' size 512.0 reuse  autoextend off", d.data_file_clause())

    def test_as_dict(self):
        d = Datafile('/path/to/dbf', 512, False)
        self.assertDictEqual({'path': '/path/to/dbf', 'size': '512.0', 'autoextend': False}, d.asdict())

        d = Datafile('/path/to/dbf', 512, True)
        self.assertDictEqual({'path': '/path/to/dbf', 'size': '512.0', 'autoextend': True}, d.asdict())

        d = Datafile('/path/to/dbf', 512, True, '1M', '10M')
        self.assertDictEqual(
            {'path': '/path/to/dbf', 'size': '512.0', 'autoextend': True, 'nextsize': '1.0M', 'maxsize': '10.0M'},
            d.asdict())


class TestFileType(unittest.TestCase):
    type_big = FileType(True)
    type_small = FileType(False)

    def test_to_string(self):
        self.assertEqual('bigfile', str(self.type_big))
        self.assertEqual('smallfile', str(self.type_small))

    def test_equals(self):
        type_s_too = FileType(False)
        self.assertNotEqual(self.type_big, self.type_small)
        self.assertEqual(self.type_small, type_s_too)
        self.assertNotEqual(self.type_big, 'foo')

    def test_is_big(self):
        self.assertTrue(self.type_big.is_bigfile())
        self.assertFalse(self.type_small.is_bigfile())


class TestContentType(unittest.TestCase):
    perm = ContentType('permanent')
    undo = ContentType('undo')
    temp = ContentType('temp')

    def test_to_string(self):
        self.assertEqual('permanent', str(self.perm))
        self.assertEqual('undo', str(self.undo))
        self.assertEqual('temp', str(self.temp))

    def test_equals(self):
        other_perm = ContentType('permanent')
        self.assertEqual(self.perm, other_perm)
        self.assertNotEqual(self.perm, self.undo)
        self.assertNotEqual(self.perm, self.temp)
        self.assertNotEqual(self.perm, 'foo')

    def test_create_clause(self):
        self.assertEqual('', self.perm.create_clause())
        self.assertEqual('undo', self.undo.create_clause())
        self.assertEqual('temporary', self.temp.create_clause())

    def test_datafile_clause(self):
        self.assertEqual('datafile', self.perm.datafile_clause())
        self.assertEqual('datafile', self.undo.datafile_clause())
        self.assertEqual('tempfile', self.temp.datafile_clause())


if __name__ == '__main__':
    unittest.main()
