#!/usr/bin/env python3
"""This script filters logs"""
from os import getenv
import re
from logging import Logger, INFO, LogRecord, Formatter
from mysql.connector import connect, connection
from typing import List
import logging

patterns = {
    'extract': lambda x, y: r'(?P<field>{})=[^{}]*'.format('|'.join(x), y),
    'replace': lambda x: rf'\g<field>={x}',
}
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
    fields: List[str], redaction: str, message: str, separator: str,) -> str:
    """Filters log line"""
    extract, replace = (patterns["extract"], patterns["replace"])
    return re.sub(extract(fields, separator), replace(redaction), message)


def get_db() -> connection.MySQLConnection:
    """ Creates connector to database"""
    db_host = getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = getenv("PERSONAL_DATA_DB_NAME", "")
    db_user = getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_pwd = getenv("PERSONAL_DATA_DB_PASSWORD", "")
    connection = connect(
        host=db_host,
        port=3306,
        user=db_user,
        password=db_pwd,
        database=db_name,
    )
    return connection
    


def get_logger() -> Logger:
    """ Creates new logger for user data"""
    logger = logging.getLogger("user_data")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.setLevel(INFO)
    logger.propagate = False
    logger.addHandler(stream_handler)
    return logger


def main():
    """Logs user information in a table"""
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    columns = fields.split(',')
    query = f"SELECT {fields} FROM users;"
    info_logger = get_logger()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            record = map(lambda x: f'{x[0]}={x[1]}', zip(columns, row),)
            message = '{}'.format('; '.join(list(record)))
            args = ("user_data", INFO, None, None, message, None, None)
            log_record = LogRecord(*args)
            info_logger.handle(log_record)


class RedactingFormatter(Formatter):
    """ Redacting formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    FORMAT_FIELDS = ('name', 'levelname', 'asctime', 'message')
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactiongFromatter, self).__init__(self.FORMAT)
        self.fields = fields
    
    def format(self, record: LogRecord) -> str:
        """Formats LogRecord"""
        msg = super(RedactingFormatter, self).format(record)
        text = filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)
        return text


if __name__ == "__main__":
    main()
