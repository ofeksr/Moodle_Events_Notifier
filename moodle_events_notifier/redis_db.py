import json

from redis import Redis, ConnectionPool

from exceptions import logging, sys

LOG = logging.getLogger('MyRedis.Logger')
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)


class MyRedis:
    def __init__(self, db: int = 0):
        LOG.debug('Initializing MyRedis object')
        self.__pool = ConnectionPool(host='localhost', port=6379, db=db, decode_responses=True)
        self.r = Redis(connection_pool=self.__pool)
        LOG.info('MyRedis object created successfully')

    def check_if_event_exists(self, event_id: int):
        return self.r.exists(event_id)

    def count_events(self):
        return self.r.dbsize()

    def insert_event(self, event_id: int, event_details: dict):
        self.r.hmset(event_id, event_details)
        LOG.info(f'{event_id} added to db')

    def get_event_details(self, event_id: int):
        return self.r.hgetall(event_id)

    def get_all_events(self):
        keys = self.r.scan()[1]
        d = {}
        for key in keys:
            d[key] = self.r.hgetall(key)
        return d

    def backup_db(self):
        self.r.bgsave()
        LOG.info('Database dump backup file created')
        pass

    def _clean_db(self):
        self.r.flushdb()
        LOG.info('Database FLUSHED!')
        return True

    def _load_data(self):
        with open('database/moodle_db.json', encoding='utf-8') as f:
            moodle_data = json.load(f)
        with self.r.pipeline() as pipe:
            for event_id, event_details in moodle_data.items():
                pipe.hmset(event_id, event_details)
            pipe.execute()


# if __name__ == '__main__':
#     r = MyRedis()
#     r._clean_db()
#     r._load_data()
#     r.get_all_events()
#     print(r.get_all_events())
