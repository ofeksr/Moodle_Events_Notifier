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

    def test_order_list_items_by_date(self):
        self.moodle._check_agent_connection(keep=True)
        self.assertTrue(self.moodle.keep.order_list_items_by_date(list_id=tests_config.trash_list_id),
                        msg='failed to order list')

    def test_send_email(self):
        self.moodle.get_events(tests_config.username, tests_config.password)

        self.assertTrue(self.moodle.send_email_report(emails=[tests_config.my_email], weekly_report=False),
                        msg='Failed to send emails')

    def test_send_email_with_all_events(self):
        self.assertTrue(
            self.moodle.send_email_with_all_events(tests_config.username, tests_config.password,
                                                   emails=[tests_config.my_email]))

    def test_rebuild_db(self):
        self.assertTrue(
            self.moodle.rebuild_db_with_all_events(username=tests_config.username, password=tests_config.password,
                                                   list_id=tests_config.trash_list_id, skip_calendar=True))


if __name__ == '__main__':
    unittest.main()
