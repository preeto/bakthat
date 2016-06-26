# -*- encoding: utf-8 -*-
import logging
import re
import peewee
from datetime import timedelta

from bakthat.conf import config, load_config, DATABASE

log = logging.getLogger(__name__)


def _timedelta_total_seconds(td):
    """Python 2.6 backward compatibility function for timedelta.total_seconds.

    :type td: timedelta object
    :param td: timedelta object

    :rtype: float
    :return: The total number of seconds for the given timedelta object.

    """
    if hasattr(timedelta, "total_seconds"):
        return getattr(td, "total_seconds")()

    # Python 2.6 backward compatibility
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / float(10**6)


def _interval_string_to_seconds(interval_string):
    """Convert internal string like 1M, 1Y3M, 3W to seconds.

    :type interval_string: str
    :param interval_string: Interval string like 1M, 1W, 1M3W4h2s...
        (s => seconds, m => minutes, h => hours, D => days, W => weeks, M => months, Y => Years).

    :rtype: int
    :return: The conversion in seconds of interval_string.

    """
    interval_exc = "Bad interval format for {0}".format(interval_string)
    interval_dict = {"s": 1, "m": 60, "h": 3600, "D": 86400,
                     "W": 7*86400, "M": 30*86400, "Y": 365*86400}

    interval_regex = re.compile("^(?P<num>[0-9]+)(?P<ext>[smhDWMY])")
    seconds = 0

    while interval_string:
        match = interval_regex.match(interval_string)
        if match:
            num, ext = int(match.group("num")), match.group("ext")
            if num > 0 and ext in interval_dict:
                seconds += num * interval_dict[ext]
                interval_string = interval_string[match.end():]
            else:
                raise Exception(interval_exc)
        else:
            raise Exception(interval_exc)
    return seconds

def _get_database():
    """Determine database in use and credentials if required."""
    database = None
    conf = config.get('default')

    if conf.get("database_type"):
        database_type = conf.get("database_type")

        if database_type == "mysql":
            if conf.get("database_host") and conf.get("database_name") and conf.get("database_user") and conf.get("database_pass") and conf.get("database_port"):
                database_host = conf.get("database_host")
                database_name = conf.get("database_name")
                database_user = conf.get("database_user")
                database_pass = conf.get("database_pass")
                database_port = conf.get("database_port")

                database = peewee.MySQLDatabase(database_name, host=database_host, port=database_port, user=database_user, passwd=database_pass)
            else:
                log.error("You must specify all config options if using mysql database.")

        if database_type == 'sqlite':
            database = peewee.SqliteDatabase(DATABASE)
    else:
        log.info("Defaulting to using SQLITE.")
        database = peewee.SqliteDatabase(DATABASE)

    return database
