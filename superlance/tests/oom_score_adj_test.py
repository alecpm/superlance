import unittest
from superlance.compat import StringIO


class OOMScoreAdjTests(unittest.TestCase):

    def _getTargetClass(self):
        from superlance.oom_score_adj import OOMScoreAdj
        return OOMScoreAdj

    def _makeOne(self, *opts):
        return self._getTargetClass()(*opts)

    def setUp(self):
        import tempfile
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tempdir)

    def _makeOnePopulated(self, programs, any, score=-1000, response=None):
        prog = self._makeOne(programs, any, score)
        prog.stdin = StringIO()
        prog.stdout = StringIO()
        prog.stderr = StringIO()
        return prog

    def test_runforever_not_process_state_running(self):
        programs = ['foo', 'bar', 'baz_01']
        any = None
        prog = self._makeOnePopulated(programs, any)
        prog.stdin.write('eventname:PROCESS_STATE_STARTED len:0\n')
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertEqual(prog.stderr.getvalue(), 'non-running event\n')
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_wrong_process(self):
        programs = ['foo']
        any = None
        prog = self._makeOnePopulated(programs, any)
        payload = ('processname:bar groupname:group1 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertEqual(prog.stderr.getvalue(), 'non-matching process\n')
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_wrong_group_process(self):
        programs = ['group1:bar']
        any = None
        prog = self._makeOnePopulated(programs, any)
        payload = ('processname:bar groupname:group2 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertEqual(prog.stderr.getvalue(), 'non-matching process\n')
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_all(self):
        programs = []
        any = True
        prog = self._makeOnePopulated(programs, any)
        payload = ('processname:bar groupname:group1 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertIn('set oom_score_adj for process bar to -1000\n',
                      prog.stderr.getvalue())
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_matching_process(self):
        programs = ['bar']
        any = None
        prog = self._makeOnePopulated(programs, any)
        payload = ('processname:bar groupname:group1 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertIn('set oom_score_adj for process bar to -1000\n',
                      prog.stderr.getvalue())
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_matching_group_process(self):
        programs = ['group1:bar']
        any = None
        prog = self._makeOnePopulated(programs, any)
        payload = ('processname:bar groupname:group1 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertIn('set oom_score_adj for process bar to -1000\n',
                      prog.stderr.getvalue())
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

    def test_runforever_custom_score(self):
        programs = ['foo']
        any = None
        score = -100
        prog = self._makeOnePopulated(programs, any, score)
        payload = ('processname:foo groupname:group1 from_state:STARTING '
                   'pid:-64444')
        prog.stdin.write(
            'eventname:PROCESS_STATE_RUNNING len:%s\n' % len(payload)
        )
        prog.stdin.write(payload)
        prog.stdin.seek(0)
        prog.runforever(test=True)
        self.assertIn('set oom_score_adj for process foo to -100\n',
                      prog.stderr.getvalue())
        self.assertEqual(prog.stdout.getvalue(),
                         b'READY\nRESULT 2\nOK')

if __name__ == '__main__':
    unittest.main()
