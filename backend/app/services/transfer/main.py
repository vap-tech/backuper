import os
from redis import Redis

from .rsyncwrap.main import rsyncwrap


class Transfer:
    """
    Перемещает файл с одного сервера на другой используя rsync.

    Прогресс доступен в redis:
        --direction: - направление download/upload
        --transferred_bytes: передано байт,
        --percent: процент переданного,
        --transfer_speed: скорость,
        --transfer_speed_unit: единицы скорости,
        --time: оставшееся время(затраченное время если завершено),
        --is_completed_stats: флаг завершения,

    Если обертка rsync вернула ошибку, текст ошибки сохраняется в атрибуте .error

    :param source: Путь к исходному файлу host:/path/to/file
    :param destination: Путь к директории назначения host:/path/to/dir
    :param redis_url: Адрес сервера redis
    :param redis_port: Порт redis (Опционален)
    :param redis_db: Номер db redis (Опционален)
    """

    def __init__(self, source, destination, redis_url, redis_port=6379, redis_db=0):
        self.file = './' + source.split('/')[-1]
        self.source = source
        self.destination = destination
        self.r = Redis(host=redis_url, port=redis_port, db=redis_db)
        self.error = []

    def __del__(self):
        self.r.set(name='direction', value='free')
        self.r.close()
        if os.path.exists(self.file):
            os.remove(self.file)

    def _transfer(self, source: str, dest: str, direction: str) -> bool:
        for update in rsyncwrap(source, dest):
            if update[0] == 'OK':
                self.r.set(name='direction', value=direction)
                for key, value in update[1].items():
                    self.r.set(key, str(value))

            elif update[0] == 'ERROR':
                self.error.append(update[1])

        return not self.error

    def download(self) -> bool:
        return self._transfer(self.source, './', 'download')

    def upload(self) -> bool:
        return self._transfer(self.file, self.destination, 'upload')
