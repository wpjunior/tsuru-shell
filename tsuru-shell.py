#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Wilson Júnior <wilsonpjunior@gmail.com>

import cmd
import sys
import os
import subprocess
import re

from optparse import OptionParser


class Historic(object):
    MAX_LENGTH = 10

    def __init__(self):
        self.config_path = os.path.expanduser('~/.tsuru_shell_history')
        self.commands = []

        if os.path.exists(self.config_path):
            self.read_config_path()

    def read_config_path(self):
        with open(self.config_path, 'rb') as f:
            self.commands = f.read().split('\n')

        self.current_pos = len(self.commands) - 1

    def write_config_path(self):
        with open(self.config_path, 'wb') as f:
            f.write('\n'.join(self.commands))

    def put(self, command):
        self.commands.append(command)

        if len(self.commands) > self.MAX_LENGTH:
            self.commands.pop(0)

        self.current_pos = len(self.commands) - 1
        self.write_config_path()

    def previous(self):
        if self.current_pos > 0:
            self.current_pos -= 1

        return self.commands[self.current_pos]

    def next(self):
        if self.current_pos < len(self.commands) - 1:
            self.current_pos += 1

        return self.commands[self.current_pos]


def do_command(name, command_alias=None):
    def f(self, line):
        command = 'tsuru %s -a %s %s' % (name, self.application, line)

        process = subprocess.Popen(
            command, shell=True)
        retcode = process.wait()


    return f


def help_command(name, command_alias=None):
    def f(self):
        process = subprocess.Popen(
            'tsuru help %s' % name, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        out, err = process.communicate()
        out = out.decode("utf-8")
        out = re.sub(r'tsuru version [0-9\\.]+', '', out)
        out = out.replace('Usage: tsuru', 'Usage:')
        out = out.replace('[--app appname]', '')
        out = out.replace(
            "If you don't provide the app name, tsuru will try to guess it.", '')
        out = re.sub('[\n]{2,}', '\n\n', out)

        if command_alias:
            out = out.replace(name, command_alias)

        sys.stdout.write(out.strip())
        sys.stdout.write('\n')
        sys.stdout.flush()

    return f


def colorize(text, color):
    """"
    Black       0;30     Dark Gray     1;30
    Blue        0;34     Light Blue    1;34
    Green       0;32     Light Green   1;32
    Cyan        0;36     Light Cyan    1;36
    Red         0;31     Light Red     1;31
    Purple      0;35     Light Purple  1;35
    Brown       0;33     Yellow        1;33
    Light Gray  0;37     White         1;37
    """
    return '\033[%sm%s\033[0m' % (color, text)


class TsuruShell(cmd.Cmd):
    intro = 'Welcome to Tsuru shell\nif you have any question please type help'

    SHELL_MULTI_MODE = 'multi'
    SHELL_ONCE_MODE = 'once'

    def __init__(self, application, *args, **kwargs):
        super(TsuruShell, self).__init__(*args, **kwargs)
        # self.historic = Historic()
        self.application = application
        self.counter = 1
        self.current_path = self.get_current_path()

        self.mode = TsuruShell.SHELL_ONCE_MODE

    def get_current_path(self):
        commands = ['tsuru', 'run', '-a', self.application, '-o', 'pwd']
        p = subprocess.Popen(commands,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()

        return out.strip().decode("utf-8")

    def do_run(self, line):
        commands = ['tsuru', 'run', '-a', self.application]

        if self.mode == TsuruShell.SHELL_ONCE_MODE:
            commands.append('-o')

        run_command = 'cd %s && %s' % (self.current_path, line)
        commands.append(run_command)
        p = subprocess.Popen(commands)
        retval = p.wait()

        if retval != 0:
            sys.exit(1)

    def do_exit(self, line):
        sys.exit(0)

    def do_cd(self, path=None):
        if not path:
            return self.reset_pwd()

        self.current_path = os.path.abspath(os.path.join(
            self.current_path, path))

    def do_once_mode(self, line):
        self.mode = TsuruShell.SHELL_ONCE_MODE
        print(
            'The commands will run in only one unit of the app,' +
            ' and prints the output.')

    def do_multi_unit_mode(self, line):
        self.mode = TsuruShell.SHELL_MULTI_MODE
        print(
            'The commands will run in all instances of the app,' +
            ' and prints the output.')

    def postcmd(self, stop, line):
        self.counter += 1

    def help_cd(self):
        print("Usage: cd [PATH]")

    def do_pwd(self, line):
        print(self.current_path)

    def reset_pwd(self):
        self.current_path = '/'

    do_restart = do_command('restart')
    help_restart = help_command('restart')

    do_start = do_command('start')
    help_start = help_command('start')

    do_stop = do_command('stop')
    help_stop = help_command('stop')

    do_env_set = do_command('env-set', "env_set")
    help_env_set = help_command('env-set', "env_set")

    do_env_unset = do_command('env-unset', "env_unset")
    help_env_unset = help_command('env-unset', "env_unset")

    do_env = do_command('env-get', "env")
    help_env = help_command('env-get', "env")

    do_log = do_command('log')
    help_log = help_command('log')

    do_version = do_command('version')
    help_version = help_command('version')

    do_info = do_command('info')
    help_info = help_command('info')

    do_unit_add = do_command('unit-add', 'unit_add')
    help_unit_add = help_command('unit-add', 'unit_add')

    do_unit_remove = do_command('unit-remove', 'unit_remove')
    help_unit_remove = help_command('unit-remove', 'unit_remove')

    do_set_cname = do_command('set-cname', 'set_cname')
    help_set_cname = help_command('set-cname', 'set_cname')

    do_unset_cname = do_command('unset-cname', 'unset_cname')
    help_unset_cname = help_command('unset-cname', 'unset_cname')

    def do_EOF(self, line):
        sys.stdout.write('\n')
        sys.exit(0)

    def default(self, line):
        self.do_run(line)

    @property
    def prompt(self):
        return '%s:%s:%s (%s)$ ' % (
            colorize(self.application, '1;34'),
            colorize(self.mode, '0;31'),
            colorize(self.current_path, '0;32'),
            colorize(self.counter, '1;34'))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--app", dest="app",
                      help="Application name", metavar="APP")

    (options, args) = parser.parse_args()

    if not options.app:
        print("Please provide the app name")
        sys.exit(1)

    shell = TsuruShell(application=options.app)
    shell.cmdloop()
