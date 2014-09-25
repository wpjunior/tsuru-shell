#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Wilson Júnior <wilsonpjunior@gmail.com>

import cmd
import sys
import os
import subprocess
import re
import readline

from optparse import OptionParser


class TsuruShellType(type):

    def __new__(cls, name, bases, attrs):
        proxy_aliases = attrs.get('proxy_aliases', {})

        for command in attrs.get('proxy_commands', []):

            if command in proxy_aliases:
                command_alias = proxy_aliases[command]
            elif '-' in command:
                command_alias = command.replace('-', '_')
            else:
                command_alias = None

            attrs['do_%s' % command_alias or command] = cls.do_command(
                command, command_alias)
            attrs['help_%s' % command_alias or command] = cls.help_command(
                command, command_alias)

        return type(name, bases, attrs)

    def do_command(name, command_alias=None):
        def f(self, line):
            command = 'tsuru %s -a %s %s' % (name, self.application, line)
            os.system(command)

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


class TsuruShell(cmd.Cmd, metaclass=TsuruShellType):

    intro = 'Welcome to Tsuru shell\nif you have any question please type help'

    SHELL_MULTI_MODE = 'multi'
    SHELL_ONCE_MODE = 'once'
    SHELL_MAX_HISTORY = 20

    proxy_commands = ('restart', 'start', 'stop', 'env-set', 'env-unset',
                      'env-get', 'version', 'app-info')
    proxy_aliases = {
        'app-info': 'info',
        'env-get': 'env'
    }

    def __init__(self, application, *args, **kwargs):
        super(TsuruShell, self).__init__(*args, **kwargs)
        self.application = application
        self.counter = 1
        self.current_path = self.get_current_path()

        self.history_dir = os.path.expanduser('~/.tsuru_shell/')
        self.history_path = os.path.join(
            self.history_dir, '%s.historic' % application)

        if os.path.exists(self.history_path):
            readline.read_history_file(self.history_path)

        readline.set_history_length(self.SHELL_MAX_HISTORY)
        self.mode = TsuruShell.SHELL_ONCE_MODE

    def get_current_path(self):
        commands = ['tsuru', 'run', '-a', self.application, '-o', 'pwd']
        p = subprocess.Popen(commands,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()

        return out.strip().decode("utf-8").splitlines()[0]

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

        if not os.path.exists(self.history_dir):
            os.mkdir(self.history_dir)

        readline.write_history_file(self.history_path)

    def help_cd(self):
        print("Usage: cd [PATH]")

    def do_pwd(self, line):
        print(self.current_path)

    def reset_pwd(self):
        self.current_path = '/'

    def do_EOF(self, line):
        sys.stdout.write('\n')
        sys.exit(0)

    def default(self, line):
        self.do_run(line)

    def colorize(self, text, color):
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

    @property
    def prompt(self):
        return '%s:%s:%s (%s)$ ' % (
            self.colorize(self.application, '1;34'),
            self.colorize(self.mode, '0;31'),
            self.colorize(self.current_path, '0;32'),
            self.colorize(self.counter, '1;34'))

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
