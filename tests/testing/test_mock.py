import unittest

from testing import mock

class TestMockFunction(unittest.TestCase):
    def test_init_state(self):
        m = mock.MockFunction(lambda a,b,c: a+b+c)
        self.assertEqual(m.call_count, 0)
        self.assertEqual(m.called, False)
        self.assertEqual(m.call_args, None)
        self.assertEqual(m.call_args_list, [])

    def test_bind_call_args(self):
        m = mock.MockFunction(lambda a,b,c: a+b+c)
        m(1,2,3)

        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.called, True)
        self.assertEqual(m.call_args, dict(a=1,b=2,c=3))
