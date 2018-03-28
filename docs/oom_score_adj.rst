:command:`oom_score_adj` Documentation
======================================

:command:`oom_score_adj` is a supervisor "event listener", intended to be
subscribed to ``PROCESS_STATE_EXITED`` events. When :command:`oom_score_adj`
receives that event, and the transition is "unexpected", :command:`oom_score_adj`
sends an email notification to a configured address.

:command:`oom_score_adj` is incapable of monitoring the process status of processes
which are not :command:`supervisord` child processes.

:command:`oom_score_adj` is a "console script" installed when you install
:mod:`superlance`.  Although :command:`oom_score_adj` is an executable program, it
isn't useful as a general-purpose script:  it must be run as a
:command:`supervisor` event listener to do anything useful.

Command-Line Syntax
-------------------

.. code-block:: sh

   $ oom_score_adj [-p processname] [-a] [-s score]

.. program:: oom_score_adj

.. cmdoption:: -p <process_name>, --program=<process_name>

   Set linux `oom_score_adj` the specified :command:`supervisord` child
   process and when the process transitions to the ``RUNNING`` state.

   This option can be provided more than once to have :command:`oom_score_adj`
   monitor more than one program.

   To monitor a process which is part of a :command:`supervisord` group,
   specify its name as ``group_name:process_name``.

.. cmdoption:: -a, --any

   Set linux `oom_score_adj` when any :command:`supervisord` child process
   transitions to the ``RUNNING`` state.

   Overrides any ``-p`` parameters passed in the same :command:`oom_score_adj`
   process invocation.

.. cmdoption:: -s <scorw>, --score=<score>

   Specify a score adjustment for the linux the OOM killer.
   The default score of ``-1000`` disables the OOM killer for the process.


Configuring :command:`oom_score_adj` Into the Supervisor Config
---------------------------------------------------------------

An ``[eventlistener:x]`` section must be placed in :file:`supervisord.conf`
in order for :command:`oom_score_adj` to do its work. See the "Events"
chapter in the Supervisor manual for more information about event listeners.

The following example assumes that :command:`oom_score_adj` is on your system
:envvar:`PATH`.

.. code-block:: ini

   [eventlistener:oom_score_adj]
   command=oom_score_adj -p program1 -p group1:program2 -s -100
   events=PROCESS_STATE_RUNNING
