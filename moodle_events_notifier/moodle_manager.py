"""
Web Scrap Moodle events needed to be complete.
Notify by email, and sync them to Google Keep & Calendar to track your homework progress
and never forget about applying tasks on time.
"""

import re
import urllib.parse
from datetime import datetime, timedelta

import pyshorteners
import requests
import yagmail
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from database import config
from exceptions import create_logger, WebScrapEvents
from google_agents import GoogleKeepAgent, GoogleCalendarAgent
from redis_db import MyRedis

LOG = create_logger()


def bitly_link(url: str):
    token = config.bitly_token
    s = pyshorteners.Shortener('Bitly', bitly_token=token)
    bitly_url = s.short(url)
    return bitly_url


def create_gcal_link(date: str, summary: str, description: str) -> str:
    """date format: 20191206/20191207 (year+month+day -> today/next day)"""
    encoded_summary = urllib.parse.quote(summary.encode('utf-8'))
    g_cal_link = f"https://www.google.com/calendar/render?action=TEMPLATE&text=" \
                 f"{encoded_summary}&dates={date}&details={description}"
    href_link = bitly_link(g_cal_link)
    html_template = f'<a href="{href_link}" target="_blank" rel="nofollow"> <br> Add to Google Calendar </a>'
    return html_template


class MoodleManager:
    def __init__(self, redis_db: int = 0):
        LOG.debug('Initializing MoodleManager object')

        self.db = MyRedis(db=redis_db)

        self.events_to_keep = []  # for google keep agent usage
        self.g_links_for_today = []  # for email report usage
        # both have same number of items

        self.events_to_calendar = {}  # for google calendar usage

        self.weekly_events = []  # for email report usage
        self.g_links_for_weeklies = []  # for email report usage
        # both have same number of items

        self.all_events = []

        self.calendar = None
        self.keep = None

        LOG.info('MoodleManager object created successfully')

    @staticmethod
    def login_to_moodle(driver, username, password):
        username_field = driver.find_element_by_id('username')
        username_field.clear()
        username_field.send_keys(username)

        password_field = driver.find_element_by_id('password')
        password_field.clear()
        password_field.send_keys(password)

        driver.find_element_by_id('loginbtn').click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'instance-283000-header')))
        LOG.info('Logged in successfully to Moodle Account')

    def get_events(self, username: str, password: str, weekly_report: bool = False, all_events: bool = False):
        """
        Web Scrap events that needed to be done in Moodle website.
        If event not in database it will be update there, and added to self.events_to_add for google keep agent usage.
        :return: tuple
        """
        LOG.debug('Trying to web scrap events with web driver')
        url = 'https://online.shenkar.ac.il/login/index.php'

        c_options = Options()  # Options for web driver silent run in background.
        c_options.headless = True
        c_options.add_argument("--log-level=3")

        try:
            # remove options=c_options for normal web driver run with opening screen.
            driver = Chrome(options=c_options)
            driver.get(url)
            LOG.info('URL opened in web driver')

            self.login_to_moodle(driver, username, password)

            events = driver.find_elements_by_class_name('event')
            for event in events:
                # get event details
                event_link = event.find_element_by_xpath('a[@data-type="event"]').get_attribute('href')
                event_id = event_link.split('_')[-1]
                event_date_time = event.find_element_by_class_name('date').text

                # format date of event
                date = event_date_time.split(', ')[0]
                try:
                    formatted_date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:  # date is tomorrow or today
                    if 'מחר' in date:
                        formatted_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
                    else:  # if 'היום' in date
                        formatted_date = datetime.today().strftime('%Y-%m-%d')

                LOG.info(f'Got event #{event_id} : {event_link}')

                new_event_flag = True if not self.db.check_if_event_exists(event_id) else False
                add_to_weekly_flag = False

                if not new_event_flag:
                    LOG.info(f'Event #{event_id} already exists in database')

                    if weekly_report:
                        # check if need to add to weekly report
                        event_date = datetime.strptime(formatted_date, '%Y-%m-%d')
                        today_check = datetime.now()
                        plus_week = today_check + timedelta(days=9)
                        if today_check <= event_date <= plus_week:
                            # need to add to weekly report
                            add_to_weekly_flag = True
                        if not all_events:
                            # not new and no need to add to weekly report
                            continue
                    if not all_events:
                        # not new and no need to add to weekly report
                        continue

                else:
                    # if new event, check if also need to add to weekly report
                    if weekly_report:
                        # check if need to add to weekly report
                        event_date = datetime.strptime(formatted_date, '%Y-%m-%d')
                        today_check = datetime.now()
                        plus_week = today_check + timedelta(days=9)
                        if today_check <= event_date <= plus_week:
                            add_to_weekly_flag = True

                # fetch event description
                pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4}, \d{2}:\d{2}')
                summary = re.sub(pattern, '', event.text).strip()

                # get event subject
                driver.execute_script(f"window.open('{event_link}');")
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'container-fluid')))
                subject = driver.find_element_by_xpath(
                    '//*[@id="page-header"]/div/div/div[2]/div[1]/div/a/div/div/h1').text
                driver.switch_to.window(driver.window_handles[0])

                bitly_url = bitly_link(event_link)

                if all_events:
                    self.all_events.append(f'{subject} - {event.text}: {bitly_url}')
                    LOG.info(f'Event #{event_id} added to all events email template')
                    continue

                if add_to_weekly_flag:
                    # add event to weekly event list template
                    self.weekly_events.append(f'{subject} - {event.text}: {bitly_url}')

                    # add event to gcal link list for email report
                    date_datetime_f = datetime.strptime(formatted_date, '%Y-%m-%d')
                    fixed_date = f"{date_datetime_f.strftime('%Y%m%d')}" \
                                 f"/{(date_datetime_f + timedelta(days=1)).strftime('%Y%m%d')}"
                    self.g_links_for_weeklies.append(
                        create_gcal_link(
                            date=fixed_date,
                            summary=f'{subject} - {summary}',
                            description=bitly_url
                        )
                    )

                    LOG.info(f'Event #{event_id} added to weekly report email template')

                if new_event_flag:
                    # add event to db
                    d = {
                        'subject': subject,
                        'text': summary,
                        'date': formatted_date,
                        'link': bitly_url
                    }
                    self.db.insert_event(event_id=event_id, event_details=d)

                    #  add event to calendar
                    self.events_to_calendar[formatted_date] = {
                        'summary': f'{subject} - {summary}',
                        'description': bitly_url,
                    }

                    #  add event to keep
                    self.events_to_keep.append(f'{subject} - {event.text}: {bitly_url}')

                    # add event to gcal link for email report
                    date_datetime_f = datetime.strptime(formatted_date, '%Y-%m-%d')
                    fixed_date = f"{date_datetime_f.strftime('%Y%m%d')}" \
                                 f"/{(date_datetime_f + timedelta(days=1)).strftime('%Y%m%d')}"
                    self.g_links_for_today.append(
                        create_gcal_link(
                            date=fixed_date,
                            summary=f'{subject} - {summary}',
                            description=bitly_url
                        )
                    )

                    LOG.info(f'Event #{event_id} added to database')

            driver.quit()
            LOG.info(f'New Events={len(self.events_to_keep)}, Weekly Events={len(self.weekly_events)}, '
                     f'Total Events in Database={self.db.count_events()}, All Events={len(self.all_events)}')
            return self.events_to_keep, self.events_to_calendar

        except Exception as e:
            LOG.exception(f'Failed to web scrap for events with web driver')
            raise WebScrapEvents('Failed to web scarp events', e)

    def send_email_report(self, emails: list, weekly_report: bool = False, all_events: bool = False):

        # generate cat photo
        cat_img_link = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url']

        yag = yagmail.SMTP(config.sender_mail, config.sender_password)
        contents = []

        if weekly_report and len(self.events_to_keep) == 0:
            subject = 'שיעורי בית איזה כיף'
            contents.append(
                '<body dir="rtl">'
                '<br>'
                '<h2>'
                'הגשות לשבוע הקרוב'
                '</h2>'
                '<br>'
                f'{"<br><br>".join([x[0] + x[1] for x in zip(self.weekly_events, self.g_links_for_weeklies)])}'
                '</body>'
            )

        elif weekly_report and len(self.events_to_keep) > 0:
            subject = 'מלא שיעורי בית איזה כיף'
            contents.append(
                '<body dir="rtl">'
                '<br>'
                '<h2>'
                'התווסף לאחרונה'
                '</h2>'
                '<br>'
                f'{"<br><br>".join([x[0] + x[1] for x in zip(self.events_to_keep, self.g_links_for_today)])}'
                '</body>'
            )
            contents.append(
                '<body dir="rtl">'
                '<br>'
                '<h2>'
                'הגשות לשבוע הקרוב'
                '</h2>'
                '<br>'
                f'{"<br><br>".join([x[0] + x[1] for x in zip(self.weekly_events, self.g_links_for_weeklies)])}'
                '</body>'
            )

        elif all_events and len(self.all_events) > 0:
            subject = 'דו"ח הגשות איזה כיף'
            contents.append(
                '<body dir="rtl">'
                '<br>'
                '<h2>'
                'הגשות לתקופה הקרובה'
                '</h2>'
                '<br>'
                f'{"<br><br>".join([x for x in self.all_events])}'
                '</body>'
            )

        else:
            subject = 'הגשה חדשה איזה כיף'
            contents.append(
                '<body dir="rtl">'
                '<br>'
                '<h2>'
                'התווסף לאחרונה'
                '</h2>'
                '<br>'
                f'{"<br><br>".join([x[0] + x[1] for x in zip(self.events_to_keep, self.g_links_for_today)])}'
                '</body>'
            )

        contents.extend([
            '<body dir="rtl">'
            '<br><br>'
            'והנה חתול'
            '</body>',
            f'<center><body>'
            f'<img src={cat_img_link}'
            f' height="350" width="350"'
            f' align="middle"/>'
            f'</body></center>',
        ])

        yag.send(bcc=emails, subject=subject, contents=contents)
        LOG.info(f'email sent to {emails}')
        return True

    def _check_agent_connection(self, calendar: bool = False, keep: bool = False):
        if calendar:
            if self.calendar is None:
                self.calendar = GoogleCalendarAgent()
                self.calendar.login()

        elif keep:
            if self.keep is None:
                self.keep = GoogleKeepAgent()
                self.keep.login(email_address=config.email_address, password=config.keep_password, token=config.token)

    def insert_event_calendar(self, event_id: int = None, schedule: bool = False, delete_flag: bool = False):
        self._check_agent_connection(calendar=True)

        if event_id:
            event_to_add = self.db.get_event_details(event_id)
            self.calendar.add_events(date=event_to_add['date'],
                                     summary=event_to_add['text'],
                                     description=event_to_add['link'],
                                     delete=delete_flag)

        elif schedule:
            for key, item in self.events_to_calendar.items():
                self.calendar.add_events(date=key,
                                         summary=item['summary'],
                                         description=item['description'],
                                         delete=delete_flag)
        LOG.info('inserting event to calendar finished')
        return True

    def insert_event_keep(self, event_id: int = None, schedule: bool = False, list_id: str = None):
        if not list_id:  # for testing usage
            list_id = config.studies_hw_list_id

        self._check_agent_connection(keep=True)

        if event_id:
            event_to_add = self.db.get_event_details(event_id)
            fixed_date = datetime.strftime(datetime.strptime(event_to_add["date"], '%Y-%M-%d'), '%d/%M/%Y')
            parsed = f'{event_to_add["subject"]} - {event_to_add["text"]} {fixed_date}:' \
                     f' {event_to_add["link"]}'

            self.keep.add_events_to_list(list_id=list_id, events=[parsed], bottom=True)
            self.keep.order_list_items_by_date(list_id=list_id)

        elif schedule:
            self.keep.add_events_to_list(list_id=list_id, events=self.events_to_keep, bottom=True)
            self.keep.order_list_items_by_date(list_id=list_id)

        LOG.info('inserting event to keep finished')
        return True

    def show_events_from_db(self, event_id: int = None):
        if event_id:
            return self.db.get_event_details(event_id)
        else:
            return self.db.get_all_events()

    def send_email_with_all_events(self, username: str, password: str, emails: list):
        self.get_events(username, password, all_events=True)
        self.send_email_report(emails, all_events=True)
        LOG.info('email with all events sent.')
        return True

    def rebuild_db_with_all_events(self, username: str, password: str, list_id: str = None,
                                   skip_calendar: bool = False):
        if not list_id:  # for testing usage
            list_id = config.studies_hw_list_id

        self.db._clean_db()
        self._check_agent_connection(keep=True)
        self.keep.delete_list_items(list_id)
        # TODO need to delete google calendar events manually.
        self.get_events(username, password)
        if not skip_calendar:
            self.insert_event_calendar(schedule=True)
        self.insert_event_keep(schedule=True, list_id=list_id)
        self.db.backup_db()
        return True
