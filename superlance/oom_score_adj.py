#!/usr/bin/env python -u
##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

# A event listener meant to be subscribed to PROCESS_STATE_CHANGE
# events.  It will set the linux oom_score_adj for processes that are
# children of supervisord when they transition to the RUNNNING state.

# A supervisor config snippet that tells supervisor to use this script
# as a listener is below.
#
# [eventlistener:oom_score_adj]
# command = oom_score_adj -p foo -p group:bar -s -500
# events=PROCESS_STATE_RUNNING
import getopt
import os
import sys

from supervisor import childutils

doc = """\
oom_score_adj.py [-p processname] [-a] [-s score] URL

Options:

-p -- specify a supervisor process_name.  Set oom_score_adj on this process
      and its children when the process is started. If this process is
      part of a group, it can be specified using the
      'group_name:process_name' syntax.

-a -- Set oom_score_adj on all processes when started.  Overrides any -p
      parameters passed in the same crashmail process invocation.

-s -- The amount to adjust the OOM score by, default -1000.

The -p option may be specified more than once, allowing for
specification of multiple processes.  Specifying -a overrides any
selection of -p.

A sample invocation:

oom_score_adj.py -p program1 -p group1:program2 -s -500

"""


def usage(exitstatus=255):
    print(doc)
    sys.exit(exitstatus)


class OOMScoreAdj:

    def __init__(self, programs, any, score=-1000):

        self.programs = programs
        self.any = any
        self.score = score
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def runforever(self, test=False):
        while 1:
            # we explicitly use self.stdin, self.stdout, and self.stderr
            # instead of sys.* so we can unit test this code
            headers, payload = childutils.listener.wait(
                self.stdin, self.stdout)

            if not headers['eventname'] == 'PROCESS_STATE_RUNNING':
                # do nothing with non-RUNNING events
                childutils.listener.ok(self.stdout)
                if test:
                    self.stderr.write('non-running event\n')
                    self.stderr.flush()
                    break
                continue

            pheaders, pdata = childutils.eventdata(payload+'\n')
            pname = pheaders['processname']
            gname = pheaders['groupname']

            if (not self.any and pname not in self.programs and
                    '%s:%s' % (gname, pname) not in self.programs):
                childutils.listener.ok(self.stdout)
                if test:
                    self.stderr.write('non-matching process\n')
                    self.stderr.flush()
                    break
                continue

            pid = pheaders['pid']
            try:
                with open('/proc/%s/oom_score_adj' % pid, 'w') as procfile:
                    procfile.write('%s\n' % self.score)
            except IOError:
                self.stderr.write('could not set oom_score_adj for '
                                  'process %s:%s\n' % (pname, pid))

            self.stderr.write('set oom_score_adj for process %s to %s\n' % (
                pname, self.score
            ))
            self.stderr.flush()

            childutils.listener.ok(self.stdout)
            if test:
                break


def main(argv=sys.argv):
    short_args = "hp:a:s:"
    long_args = [
        "help",
        "program=",
        "any",
        "score=",
    ]
    arguments = argv[1:]
    try:
        opts, args = getopt.getopt(arguments, short_args, long_args)
    except getopt.GetoptError:
        usage()

    programs = []
    any = False
    score = -1000

    for option, value in opts:

        if option in ('-h', '--help'):
            usage(exitstatus=0)
            return

        if option in ('-p', '--program'):
            programs.append(value)

        if option in ('-a', '--any'):
            any = True

        if option in ('-s', '--score'):
            score = int(value)

    if 'SUPERVISOR_SERVER_URL' not in os.environ:
        sys.stderr.write('oom_score_adj must be run as a supervisor event '
                         'listener\n')
        sys.stderr.flush()
        return

    prog = OOMScoreAdj(programs, any, score)
    prog.runforever()


if __name__ == '__main__':
    main()
