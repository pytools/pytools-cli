# -*- coding: utf-8 -*-

import unittest
from .context import pytools_cli as cli


def create_test_data():
    cli.cd('~/')
    cli.mkdir('test-data')
    cli.cd('test-data')

    cli.mkdir('a')
    cli.mkdir('b')
    cli.mkdir('c')
    cli.mkdir('dir-1')
    cli.mkdir('dir-2')
    cli.mkdir('dir-3')

    cli.touch('.text')
    cli.touch('text')
    cli.touch('text.txt')

    cli.symlink('text', 'symlink-file')
    cli.symlink('a',    'symlink-dir')

    cli.cd('a')

    cli.touch('.text')
    cli.touch('text')
    cli.touch('text.txt')

    cli.touch('.file')
    cli.touch('file')
    cli.touch('file-a')
    cli.touch('file-b')
    cli.touch('file-c')
    cli.touch('file.txt')


def delete_test_data():
    cli.cd('~/')
    cli.delete('test-data')


def get_test_data_path():
    cli.cd('~/')
    cli.cd('test-data')

    return cli.cwd()


class TestSimpleCases(unittest.TestCase):

    def setUp(self):
        delete_test_data()
        create_test_data()

        self.path = get_test_data_path()
        cli.cd(self.path)

    def tearDown(self):
        delete_test_data()

    def test_file_exists(self):
        self.assertTrue(cli.file_exists('.text'))
        self.assertTrue(cli.file_exists('text'))
        self.assertTrue(cli.file_exists('text.txt'))

        # directory check
        self.assertFalse(cli.file_exists('a'))

        # symlink check
        self.assertTrue(cli.file_exists('symlink-file'))
        self.assertFalse(cli.file_exists('symlink-file', False))

        self.assertFalse(cli.file_exists('symlink-dir'))

    def test_dir_exists(self):
        self.assertTrue(cli.dir_exists('a'))
        self.assertTrue(cli.dir_exists('dir-1'))

        # file check
        self.assertFalse(cli.file_exists('a'))
        self.assertFalse(cli.file_exists('dir-1'))

        # symlink check
        self.assertTrue(cli.dir_exists('symlink-dir'))
        self.assertFalse(cli.dir_exists('symlink-dir', False))

        self.assertFalse(cli.dir_exists('symlink-file'))

    def test_symlink_exists(self):
        self.assertTrue(cli.symlink_exists('symlink-file'))
        self.assertTrue(cli.symlink_exists('symlink-dir'))

        self.assertTrue(cli.symlink_exists('symlink-file', must_point_to_file=False))
        self.assertTrue(cli.symlink_exists('symlink-file', must_point_to_file=True))

        self.assertTrue(cli.symlink_exists('symlink-file', must_point_to_dir=False))
        self.assertFalse(cli.symlink_exists('symlink-file', must_point_to_dir=True))

        self.assertTrue(cli.symlink_exists('symlink-dir', must_point_to_file=False))
        self.assertFalse(cli.symlink_exists('symlink-dir', must_point_to_file=True))

        self.assertTrue(cli.symlink_exists('symlink-dir', must_point_to_dir=False))
        self.assertTrue(cli.symlink_exists('symlink-dir', must_point_to_dir=True))

        # file check
        self.assertTrue(cli.file_exists('symlink-file'))
        self.assertFalse(cli.file_exists('symlink-file', include_symlink_to_file=False))

        # directory check
        self.assertTrue(cli.dir_exists('symlink-dir'))
        self.assertFalse(cli.dir_exists('symlink-dir', include_symlink_to_dir=False))

    def test_glob(self):
        paths = cli.glob('a/file-*')

        for path in paths:
            self.assertTrue(cli.file_exists(path))

        for path in paths:
            cli.remove(path)
            self.assertFalse(cli.file_exists(path))

    def test_compress(self):
        cli.compress('.', 'test-archive')

        self.assertTrue(cli.file_exists('test-archive*'))

        cli.compress('.', 'test-archive-2.tar.xz')

        self.assertTrue(cli.file_exists('test-archive-2.tar.xz'))

    def test_extract(self):
        cli.compress('.', 'test-archive')

        cli.extract('test-archive')
        self.assertTrue(cli.dir_exists('test-archive'))

        cli.extract('test-archive', 'arc')
        self.assertTrue(cli.dir_exists('arc'))


if __name__ == '__main__':
    unittest.main()
