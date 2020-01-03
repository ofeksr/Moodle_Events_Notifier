import os
import unittest

import moodle_manager
from tests.database import tests_config


class TestMoodleNotifier(unittest.TestCase):

    def setUp(self) -> None:
        for path in ['database', 'logs']:
            if not os.path.isdir(path):
                os.mkdir(path)

        self.moodle = moodle_manager.MoodleManager(redis_db=1)

    def tearDown(self) -> None:
        self.moodle.db._clean_db()
        self.moodle = None

    def test_short_url(self):
        url = 'https://online.shenkar.ac.il/login/index.php'
        self.assertIsInstance(moodle_manager.short_url(url),
                              str,
                              msg='Failed to get respond from short url')

    def test_redis_db(self):
        self.assertIsNotNone(self.moodle.db.count_events(),
                             msg='Failed to connect Redis database')

    def test_get_events(self):
        self.assertIsInstance(self.moodle.get_events(tests_config.username, tests_config.password),
                              tuple,
                              msg='Failed to scarp events from Moodle website')

    def test_insert_events(self):
        def keep_event():
            return self.assertTrue(
                self.moodle.insert_event_keep(schedule=True, list_id=tests_config.trash_list_id))

        def calendar_event():
            return self.assertTrue(
                self.moodle.insert_event_calendar(schedule=True, delete_flag=True))

        def sub_tests(key):
            switcher = {
                0: keep_event,
                1: calendar_event,
            }
            return switcher.get(key, 'Invalid test key')

        for i in range(2):
            with self.subTest(sub_tests(i).__name__):
                func = sub_tests(i)
                func()

    def test_send_email(self):
        self.moodle.get_events(tests_config.username, tests_config.password)

        self.assertTrue(self.moodle.send_email_report(emails=[tests_config.my_email], weekly_report=True),
                        msg='Failed to send emails')


if __name__ == '__main__':
    unittest.main()
