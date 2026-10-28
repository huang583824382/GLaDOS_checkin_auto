import importlib
import os
import unittest
from unittest.mock import Mock, patch


class CheckinTests(unittest.TestCase):
    def test_result_classification(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            cases = [
                ({'code': 0, 'message': 'OK'}, True),
                ({'code': 1, 'message': 'Checkin Repeats! Please Try Tomorrow'}, True),
                ({'code': 1, 'message': "Today's observation logged"}, True),
                ({'code': 1, 'message': 'Already checked in'}, True),
                ({'code': 1, 'message': '今天已经签到'}, True),
                ({'code': -2, 'message': '没有权限'}, False),
                ({'code': 0, 'reason': 'device-mismatch'}, False),
                ({'code': 1, 'message': 'Failure'}, False),
                (None, False),
                ([], False),
            ]
            for result, expected in cases:
                with self.subTest(module=name, result=result):
                    self.assertEqual(module.is_normal_checkin_result(result), expected)

    def test_exit_status_and_optional_failures(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            cases = [
                ([{'code': 0}], 0, None),
                ([{'code': 1, 'message': 'Checkin Repeats! Please Try Tomorrow'}], 0, None),
                ([{'code': 0}], 0, 'get_status'),
                ([{'code': 0}], 0, 'get_points'),
                ([{'code': 0}], 0, 'exchange'),
                ([{'code': -2, 'message': '没有权限'}], 1, None),
                ([None], 1, None),
                ([{'code': 0}, {'code': 1, 'message': 'Failure'}, {'code': 0}], 1, None),
            ]
            for results, expected, failure in cases:
                with self.subTest(module=name, results=results, failure=failure):
                    clients = [Mock(points='500', left_days='30') for _ in results]
                    for client, result in zip(clients, results):
                        client.checkin.return_value = result
                        client.exchange.return_value = {'code': 1, 'message': 'Failure'}
                        if failure:
                            getattr(client, failure).side_effect = ValueError('invalid response')
                    env = {
                        'GLADOS_COOKIE': '&'.join(['gld:sess=test; gld:sess.sig=test'] * len(results)),
                        'CHECKIN_MAX_ATTEMPTS': '1',
                        'CHECKIN_RETRY_DELAY_SECONDS': '0',
                    }
                    with patch.dict(os.environ, env, clear=True), \
                            patch.object(module, 'GLaDOS', side_effect=clients), \
                            patch.object(module, 'log'):
                        self.assertEqual(module.main(), expected)
                    for client in clients:
                        client.checkin.assert_called_once()

    def test_retry_then_success(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            client = Mock()
            client.checkin.side_effect = [None, {'code': 0}]
            with patch.object(module.time, 'sleep'), patch.object(module, 'log'):
                self.assertEqual(module.checkin_with_retry(client), ({'code': 0}, True))
            self.assertEqual(client.checkin.call_count, 2)

    def test_request_exception_then_success(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            client = Mock()
            client.checkin.side_effect = [RuntimeError('request failed'), {'code': 0}]
            with patch.object(module.time, 'sleep'), patch.object(module, 'log'), \
                    patch.object(module.traceback, 'print_exc'):
                self.assertEqual(module.checkin_with_retry(client), ({'code': 0}, True))
            self.assertEqual(client.checkin.call_count, 2)

    def test_failures_retry_once(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            for result in (None, {'code': 1, 'message': 'Failure'},
                           {'code': -2, 'message': '没有权限'}):
                with self.subTest(module=name, result=result):
                    client = Mock()
                    client.checkin.return_value = result
                    with patch.object(module, 'log'), patch.object(module.time, 'sleep') as sleep:
                        self.assertEqual(module.checkin_with_retry(client), (result, False))
                    self.assertEqual(client.checkin.call_count, 2)
                    sleep.assert_called_once_with(60)

    def test_success_does_not_retry(self):
        for name in ('glados', 'glados_2026'):
            module = importlib.import_module(name)
            for result in ({'code': 0}, {'code': 1, 'message': 'Already checked in'}):
                with self.subTest(module=name, result=result):
                    client = Mock()
                    client.checkin.return_value = result
                    with patch.object(module.time, 'sleep') as sleep:
                        self.assertEqual(module.checkin_with_retry(client), (result, True))
                    client.checkin.assert_called_once()
                    sleep.assert_not_called()

    def test_missing_cookie_fails(self):
        import glados
        with patch.dict(os.environ, {}, clear=True), patch.object(glados, 'log'):
            self.assertEqual(glados.main(), 1)

    def test_qinglong_propagates_result(self):
        import glados_Qinglong
        for code in (0, 1):
            with patch.object(glados_Qinglong, 'main', return_value=code):
                self.assertEqual(glados_Qinglong.start(), code)
                self.assertEqual(glados_Qinglong.main_handler(None, None), code)


if __name__ == '__main__':
    unittest.main()
