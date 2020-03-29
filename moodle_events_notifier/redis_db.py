import json

from redis import StrictRedis, ConnectionPool

from exceptions import logging, sys

LOG = logging.getLogger('MyRedis.Logger')
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)


class MyRedis:
    def __init__(self, db: int = 0):
        LOG.debug('Initializing MyRedis object')
        self.__pool = ConnectionPool(host='localhost', port=6379, db=db, decode_responses=True)
        self.r = StrictRedis(connection_pool=self.__pool)
        LOG.info('MyRedis object created successfully')

    def check_if_event_exists(self, event_id: int):
        return self.r.exists(f'event:{event_id}')

    def count_events(self):
        return len([_ for _ in (self.r.scan_iter(match='event:*'))])

    def insert_event(self, event_id: int, event_details: dict):
        self.r.hmset(f'event:{event_id}', event_details)
        LOG.info(f'{event_id} added to db')

    def get_event_details(self, event_id: int):
        return self.r.hgetall(f'event:{event_id}')

    def get_all_events(self):
        keys = self.r.scan_iter(match='event:*')
        d = {}
        for key in keys:
            d[key] = self.r.hgetall(key)
        return d

    def insert_email(self, user_name: str, family_name: str, email_address: str):
        self.r.hmset(f'user:{user_name}', {'family_name': family_name,
                                           'email_address': email_address})
        LOG.info(f'{user_name}, {family_name}; {email_address} added to db')

    def remove_email(self, user_name: str):
        self.r.hdel(f'user:{user_name}', 'email_address')
        LOG.info(f'{user_name} email removed from db')

    def get_all_emails(self, only_addresses: bool = False):
        keys = self.r.scan_iter(match='user:*')
        d = {}
        for key in keys:
            d[key] = self.r.hgetall(key)

        if only_addresses:
            return [e['email_address'] for e in d.values()]
        else:
            return d

    def backup_db(self):
        self.r.bgsave()
        LOG.info('Database dump backup file created')
        pass

    def _clean_db(self):
        self.r.flushdb()
        LOG.info('Database FLUSHED!')
        return True

    @staticmethod
    def get_moodle_data():
        with open('database/moodle_db.json', encoding='utf-8') as f:
            moodle_data = json.load(f)
        return moodle_data

    def save_events_in_redis_db(self, moodle_data):
        with self.r.pipeline() as pipe:
            for event_id, event_details in moodle_data.items():
                pipe.hmset(f'event:{event_id}', event_details)
            pipe.execute()

    def save_emails_in_redis_db(self):
        with open('database/emails.json') as f:
            with self.r.pipeline() as pipe:
                data = json.load(f)
                for name, email in data.items():
                    first, last = name.split()
                    pipe.hmset(f'user:{first}', {'last_name': last, 'email_address': email})
                pipe.execute()

    def _load_data(self):
        moodle_data = self.get_moodle_data()
        self.save_events_in_redis_db(moodle_data)
        self.save_emails_in_redis_db()

    def get_events_details(self):
        data = {}
        for event_id, event_details in self.get_all_events().items():
            data[event_id] = event_details
        return data

    @staticmethod
    def dump_events_to_json(path, data):
        with open(f'{path}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def _db_to_json(self, path: str):
        data = self.get_events_details()
        self.dump_events_to_json(path, data)


if __name__ == '__main__':
    r = MyRedis()
    # set up new updated db:
    # r._db_to_json('database/moodle_db')
    # r._clean_db()
    # r._load_data()
    ####################################
    p = r.get_all_events()
    import pprint

    pprint.pprint(p)
