#!/usr/bin/env python
# Author: Wilson Júnior <wilsonpjunior@gmail.com>

import sys
import subprocess
from optparse import OptionParser


class TsuruShell(object):

    def __init__(self, application):
        self.application = application
        self.counter = 1

    def execute_command(self, command):
        p = subprocess.Popen(['tsuru', 'run', '-a', self.application, command])
        retcode = p.wait()

        if retcode != 0:
            sys.exit(retcode)

    def run(self):
        while True:
            try:
                command = raw_input(
                    '[%s:%d] ->' % (self.application, self.counter))
            except EOFError:
                print '\n'
                break

            self.execute_command(command)
            self.counter += 1

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--app", dest="app",
                      help="Application name", metavar="APP")

    (options, args) = parser.parse_args()

    if not options.app:
        print "Please specify the application name"
        sys.exit(1)

    shell = TsuruShell(application=options.app)
    shell.run()
