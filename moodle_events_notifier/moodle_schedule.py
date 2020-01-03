import shutil
import time

from database import config
from exceptions import log_error_to_desktop
from moodle_manager import MoodleManager, LOG, datetime, json


def run_script(weekly_report: bool):

    try:

        # load emails list from json file
        with open('database/emails.json') as f:
            emails_list = list(json.load(f).values())

        moodle = MoodleManager()

        moodle.get_events(username=config.moodle_username, password=config.moodle_password, weekly_report=weekly_report)

        if len(moodle.events_to_keep) > 0 or weekly_report:
            moodle.send_email_report(emails=emails_list, weekly_report=weekly_report)

            if len(moodle.events_to_keep) > 0:
                # add events to google agents
                moodle.insert_event_calendar(schedule=True)
                moodle.insert_event_keep(schedule=True)

                # save db and backup it
                moodle.db.backup_db()

                backup_path = f'C:/Users/{config.os.getlogin()}/PycharmProjects/Backup Databases/Moodle/Redis'
                if not config.os.path.isdir(backup_path):
                    config.os.mkdir(backup_path)

                TODAY = datetime.strftime(datetime.today(), '%d.%m.%Y')
                shutil.copy2('C:/Program Files/Redis/dump.rdb',
                             f'{backup_path}/dump_{TODAY}.rdb')

            time.sleep(3.5)
            return True

        else:
            LOG.info('No new events, nor weekly report needed.')
            exit()

    except Exception:
        LOG.exception('Script not fully finished, error file created')
        log_error_to_desktop()


if __name__ == '__main__':
    if datetime.today().weekday() == 5:
        LOG.info('Today is Saturday, no need to notify about tasks.')
        exit()
    elif datetime.today().weekday() == 3:
        run_script(weekly_report=True)
    else:
        run_script(weekly_report=False)

