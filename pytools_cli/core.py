# -*- coding: utf-8 -*-

import os
from pytools_command import observe_command


def _strip(result):
    if type(result) is str:
        return result.rstrip()

    return result.output().rstrip()


def _normalize(path):
    return os.path.normpath(path)


class CLI:

    def __init__(self):
        # determine CWD upon initialization
        self._determine_cwd()

    def cwd(self, path=None):
        result = observe_command('pwd', shell=True, cwd=self._get_cwd())
        stdout = _strip(result)

        if path:
            return _normalize(stdout + '/' + path)

        return stdout

    def cud(self, path=None):
        result = observe_command(['''eval echo ~$USER'''], shell=True)
        cud = _strip(result)

        if path:
            return _normalize(cud + '/' + path)

        return cud

    def pwd(self):
        print(self._get_cwd())

    def cd(self, path=None):
        if path == '~/':
            self._set_cwd(self.cud())
            return

        if path == '/':
            self._set_cwd(_normalize(path))
            return

        normalized = _normalize(self._get_cwd() + '/' + path)

        if self.dir_exists(normalized):
            self._set_cwd(normalized)
            return

    def file_exists(self, path, include_symlink_to_file=True):
        normalized = _normalize(path)
        result = observe_command(['''[ -f {} ] && exit 0'''.format(normalized)],

                                 shell=True,
                                 cwd=self._get_cwd())

        # if path exists and it is a file, the return_value is 0, otherwise 1
        exists = result.return_value() == 0

        if not include_symlink_to_file:
            return exists and not self.symlink_exists(normalized)

        return exists

    def dir_exists(self, path, include_symlink_to_dir=True):
        normalized = _normalize(path)
        result = observe_command(['''[ -d {} ] && exit 0'''.format(normalized)],

                                 shell=True,
                                 cwd=self._get_cwd())

        # if path exists and it is a directory, the return_value is 0, otherwise 1
        exists = result.return_value() == 0

        if not include_symlink_to_dir:
            return exists and not self.symlink_exists(normalized)


        return exists

    def symlink_exists(self, path, must_point_to_file=False, must_point_to_dir=False):
        normalized = _normalize(path)
        result = observe_command(['''[ -L {} ] && exit 0'''.format(normalized)],

                                 shell=True,
                                 cwd=self._get_cwd())

        # if path exists and it is a symlink, the return_value is 0, otherwise 1
        is_symlink = result.return_value() == 0

        if must_point_to_file:
            return is_symlink and self.file_exists(normalized)

        if must_point_to_dir:
            return is_symlink and self.dir_exists(normalized)

        return is_symlink

    def exists(self, path):
        normalized = _normalize(path)

        if self.file_exists(normalized) or \
           self.dir_exists(normalized) or \
           self.symlink_exists(normalized):

            return True

        return False

    def path_exists(self, path):
        return self.exists(path)

    def cat(self, path):
        normalized = _normalize(path)
        result = observe_command(['cat {}'.format(normalized)],

                                 shell=True,
                                 cwd=self._get_cwd())

        print(result.output())

    def touch(self, file_name):
        observe_command(['touch {}'.format(file_name)],

                        shell=True,
                        cwd=self._get_cwd())

    def mkdir(self, path):
        observe_command(['mkdir -p {}'.format(path)],

                        shell=True,
                        cwd=self._get_cwd())

    def symlink(self, what_path, to_where):
        observe_command(['ln -sfn {} {}'.format(what_path, to_where)],

                        shell=True,
                        cwd=self._get_cwd())

    def create_file(self, file_name):
        return self.touch(file_name)

    def create_dir(self, path):
        return self.mkdir(path)

    def create_symlink(self, what_path, to_where):
        return self.symlink(what_path, to_where)

    def rm(self, path):
        observe_command(['rm -rf {}'.format(path)],

                        shell=True,
                        cwd=self._get_cwd())

    def remove(self, path):
        return self.rm(path)

    def delete(self, path):
        return self.rm(path)

    def cp(self, source, dest):
        observe_command(['yes | cp -rf {} {}'.format(source, dest)],

                        shell=True,
                        cwd=self._get_cwd())

    def copy(self, source, dest):
        return self.cp(source, dest)

    def mv(self, source, dest):
        observe_command(['mv {} {}'.format(source, dest)],

                        shell=True,
                        cwd=self._get_cwd())

    def move(self, source, dest):
        return self.mv(source, dest)

    def rename(self, current_name, new_path):
        self.mv(current_name, new_path)

    def glob(self, pattern):
        result = observe_command(['''
            shopt -s globstar
            ls {}
        '''.format(pattern)],
                                 shell=True,
                                 cwd=self._get_cwd())

        output = _strip(result)  # type: str
        paths = output.splitlines()  # type: list

        return paths

    def compress(self, path, archive_name):
        normalized = _normalize(path)

        if not self.exists(normalized):
            raise NotADirectoryError('The path "{}" does not exist.'.format(normalized))

        arc_name = archive_name  # type: str

        if arc_name.endswith('.tar.xz'):
            arc_name = arc_name.replace('.tar.xz', '')

        observe_command(['XZ_OPT=-9 tar -cvpJf {}.tar.xz {}'.format(arc_name, normalized)],

                        shell=True,
                        cwd=self._get_cwd())

        archive = '{}.tar.xz'.format(arc_name)

        if not self.file_exists(self.cwd(archive)):
            raise FileNotFoundError('The archive "{}" was not created.'.format(archive))

    def extract(self, archive_name, dir_to_extract=None):
        arc_name = archive_name  # type: str

        if arc_name.endswith('.tar.xz'):
            arc_name = arc_name.replace('.tar.xz', '')

        archive = '{}.tar.xz'.format(arc_name)

        if not self.file_exists(self.cwd(archive)):
            raise FileNotFoundError('Archive "{}" does not exist.'.format(archive))

        dir = arc_name

        if dir_to_extract:
            dir = _normalize(dir_to_extract)

        if not self.dir_exists(dir):
            self.create_dir(dir)

        observe_command(['tar xf {}.tar.xz -C {}'.format(arc_name, dir)],

                        shell=True,
                        cwd=self._get_cwd())

    def _determine_cwd(self):
        result = observe_command('pwd', shell=True)

        self._set_cwd(result.stdout().rstrip())

    def _get_cwd(self):
        return self._cwd

    def _set_cwd(self, cwd):
        self._cwd = cwd


cli = CLI()

cwd = cli.cwd
cud = cli.cud
pwd = cli.pwd
cd = cli.cd
file_exists = cli.file_exists
dir_exists = cli.dir_exists
symlink_exists = cli.symlink_exists
exists = cli.exists
is_file = file_exists
is_dir = dir_exists
is_symlink = symlink_exists
path_exists = cli.path_exists
cat = cli.cat
touch = cli.touch
mkdir = cli.mkdir
symlink = cli.symlink
create_file = cli.create_file
create_dir = cli.create_dir
create_symlink = cli.create_symlink
rm = cli.rm
remove = cli.remove
delete = cli.delete
cp = cli.cp
copy = cli.copy
mv = cli.mv
move = cli.move
rename = cli.rename
glob = cli.glob
compress = cli.compress
extract = cli.extract
