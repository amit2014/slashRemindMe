#!/usr/bin/env python

# Built-in imports
import calendar
from datetime import datetime, timedelta
import logging
import os
import re
import time

# Third-party dependencies
import dataset
import tweepy
import parsedatetime.parsedatetime as pdt
from pytz import timezone


# Set the Twitter credentials
TWITTER_KEY = os.environ.get('TWITTER_KEY', '')
TWITTER_SECRET = os.environ.get('TWITTER_SECRET', '')
TWITTER_TOKEN = os.environ.get('TWITTER_TOKEN', '')
TWITTER_TOKEN_SECRET = os.environ.get('TWITTER_TOKEN_SECRET', '')

DATABASE_URL = 'postgresql://postgres:postgres@%s:%s/' % (
    os.environ.get('POSTGRES_PORT_5432_TCP_ADDR'),
    os.environ.get('POSTGRES_PORT_5432_TCP_PORT'))


MAX_TWEET_LENGTH = 140
BACKOFF = 0.5  # Initial wait time before attempting to reconnect
MAX_BACKOFF = 300  # Maximum wait time between connection attempts
USERNAME = 'slashRemindMe'

# Regex to pull out the reminder message from the tweet
INPUT_MESSAGE_RE = '(["].{0,9000}["])'
REMINDER_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DEFAULT_TZ = 'UTC'

logging.basicConfig(filename='logger.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connect to the db
db = dataset.connect(DATABASE_URL)
print('DATABASE_URL=%s' % DATABASE_URL)
table = db['reminders']

# Twitter client
auth = tweepy.OAuthHandler(TWITTER_KEY, TWITTER_SECRET)
auth.set_access_token(TWITTER_TOKEN, TWITTER_TOKEN_SECRET)
api = tweepy.API(auth)

# backoff time
backoff = BACKOFF

# parsedatetime object
cal = pdt.Calendar()


def now():
    """Get the current time in UTC."""
    ts = cal.parse('now', datetime.now(timezone(DEFAULT_TZ)))[0]
    return time.strftime(REMINDER_TIME_FORMAT, ts)


def search_db():
    '''Returns a list of all rows from db that we can remind right now.'''
    now_ts = now()
    print(now_ts)
    result = db.query(('select * from reminders '
                       'where sent_tweet_id = \'\''
                       'and reminder_time::timestamp < \'%s\'::timestamp;' % now_ts))

    for row in result:
        print(row)


if __name__ == '__main__':
    print('Tweeter started...')
    search_db()
    # while True:
        # Search database for entries with reminder_time <= now and sent_tweet_id == ''
        # Send the reminder
        # Mark as sent (sent_tweet_id=tweet_id, sent_ts=now)