# -*- coding: utf-8 -*-
"""
Twitter stream

For use with victualiser, handles twitter streams.

@category   Utility
@version    $ID: 0.1.1, 2016-12-05 17:00:00 CST $;
@author     KMR
@licence    MIT (X11)
"""
import os, sys, re
import yaml, json
import argparse, errno
from datetime import datetime

import pandas as pd
from textblob import TextBlob
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

class TwitterStreamListener(StreamListener):
    def __init__(self, api=None, limit_type=None, limit=None):
        # Use the api provided or try a generic one
        self.api = api or API()
        # If we have a limit set it up
        self.limit = limit
        self.ltype = limit_type
        if self.ltype == 'count':
            self.counter = 0
        elif self.ltype == 'time':
            self.time = datetime.now()

    def on_status(self, status):
        # Avoid collecting retweets
        if hasattr(status, 'retweeted_status'):
            return

        try:
            # Check if we've hit a time limit
            if self.ltype == 'time':
                if (datetime.now() - self.time) > self.limit:
                    return False

            # Write the data out
            print(json.dumps(status._json))

            # Check if we've reached a count limit
            if self.ltype == 'count':
                self.counter += 1
                if self.counter >= self.limit:
                    return False
            return True

        except IOError as e:
            if e.errno == errno.EPIPE:
                # Broken pipe probably means the downstream consumer is gone, so just leave quietly.
                sys.stderr.close()
                sys.exit(0)
        except Exception as e:
            print('Failed on_status: ', str(e))
            pass

    def on_error(self, status):
        # See if we're rate limited, or we have a broken pipe if not just keep on going
        if status == 420:
            return False
        print(status)
        return True

class Gatherer:
    def __init__(self, filters=None):
        """
        Initialise a new tweet gatherer

        :param filters: a list of of keyword filters eg. ["political", "impeachment"]
        """
        #Load in the config
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/twitter.cfg".format(self.dir)))

        # Handle Twitter authentication and connection to the Twitter Streaming API
        self.auth = OAuthHandler(self.conf['consumer_key'], self.conf['consumer_secret'])
        self.auth.set_access_token(self.conf['access_token'], self.conf['access_token_secret'])
        self.filters = filters

    def gather(self):
        """
        gather the data from the source
        :return path: the location of all our victuals
        """
        # Initialise and configure the stream listener
        sl = TwitterStreamListener(API(self.auth), self.conf['limit_type'], self.conf['limit_count'])
        self.stream = Stream(auth=self.auth, listener=sl)

        # Pull in the stream using filters if we have them, or a global stream if not
        if self.filters:
            self.stream.filter(track=self.filters)
        else:
            # Semi-work around for the lack of a firehose
            # Note: will only work for geotagged tweets
            self.stream.filter(locations=[-180,-90,180,90])

class Chef:
    def __init__(self):
        """
        Initialise a new chef to enrich the data

        :param path: the path to a file containing raw tweets in stringified json form
        """
        self.source_re = re.compile('>(.+)</a>')

    def cook(self):
        """
        Make the data delicious
        :return: path: the output path for the file with all the nice new data
        """
        try:
            for line in sys.stdin:
                # remove leading and trailing whitespace
                line = line.strip()

                # Load the JSON and build a TextBlob for some nice text analytics
                try:
                    tweet = json.loads(line)
                except Exception as e:
                    # Line wasn't json, possible twitter errors, but ignore this anyway
                    continue

                blob = TextBlob(tweet['text'])
                m = self.source_re.search(tweet['source'])
                user_description = tweet['user']['description'].replace('\n', ' ').replace('\r', '') if tweet['user']['description'] else None

                tweet_data = {
                    'text': tweet['text'].replace('\n', ' ').replace('\r', ''),
                    'created_at': tweet['created_at'],
                    'source': m.group(1),
                    'source_full': tweet['source'],
                    'retweets': tweet['retweet_count'],
                    'favorites': tweet['favorite_count'],
                    'language': tweet['lang'],
                    'sentiment_polarity': blob.sentiment.polarity,
                    'sentiment_subjectivity': blob.sentiment.subjectivity,
                    'noun_phrases': blob.noun_phrases,
                    'user_name': tweet['user']['name'],
                    'user_screen_name': tweet['user']['screen_name'],
                    'user_description': user_description,
                    'user_location': tweet['user']['location'],
                    'user_time_zone': tweet['user']['time_zone'],
                    'user_lang': tweet['user']['lang'],
                    'user_friends': tweet['user']['friends_count'],
                    'user_followers': tweet['user']['followers_count'],
                    'user_statuses': tweet['user']['statuses_count'],
                    'user_favourites': tweet['user']['favourites_count'],
                    'user_listed': tweet['user']['listed_count'],
                    'user_verified': tweet['user']['verified'],
                    'user_protected': tweet['user']['protected'],
                    'place_type': tweet['place']['place_type'] if tweet['place'] else None,
                    'place_full_name': tweet['place']['full_name'] if tweet['place'] else None,
                    'place_country': tweet['place']['country'] if tweet['place'] else None,
                }
                # output the new data
                print("{}".format(json.dumps(tweet_data, sort_keys=True)))
        except IOError as e:
            if e.errno == errno.EPIPE:
                # Broken pipe probably means the downstream consumer is done, so just leave quietly.
                sys.stderr.close()
                sys.exit(0)
            sys.exit("Chef.cook() encountered: {}".format(str(e)))

class Waiter:
    def menu(self):
        """
        Provides a list of possible items to order
        :return: list containg string keys available for service
        """
        for line in sys.stdin:
            print(json.dumps(list(json.loads(line)), sort_keys=True))
            sys.exit(0)

    def serve(self, items=None, table=None):
        """
        Collects cooked data from the chef and serves up the result
        :param items: the a list of keys to produce data for
        :param table: the output file location
        """
        tweets = []
        # Open the input file and load the json into a DataFrame and then a list
        for line in sys.stdin:
            df = pd.io.json.json_normalize(json.loads(line))
            # If we have a filter of items drop the extra bits
            if items:
                for c in df.columns:
                    if c not in items:
                        df = df.drop(c, axis=1)
            tweets.append(df)

        # Use pandas' nice concat function to join all the frames in to one and dump everything out to a file
        dir = os.path.dirname(os.path.realpath(__file__))
        conf = yaml.safe_load(open('{}/twitter.cfg'.format(dir)))
        table = table or conf['out_loc']
        out_path = datetime.now().strftime(table.format(dir))
        pd.concat(tweets).to_csv(out_path, sep='\t', encoding='utf-8')

    def order(self, items):
        dish = {}
        for line in sys.stdin:
            rich_tweet = json.loads(line)
            component = dish
            for key in items[:-1]:
                component = component.setdefault(rich_tweet[key], {})
            component[rich_tweet[items[-1]]] = component[rich_tweet[items[-1]]] + 1 if rich_tweet[items[-1]] in component else 1
        print("{}".format(json.dumps(dish)))

def main():
    # Get some args
    description = 'Twitter stream victualiser'
    usage = '\npython victuals.py -g -f "Victuals" "Delicious"\npython victuals.py -c' \
            '\npython victuals.py -w -m\npython victuals.py -w -o "source"\n' \
            'python victuals.py -w -s "text" "language" "source" -t "/tmp/data/twitter_text_language_source"'
    parser = argparse.ArgumentParser(
        description=description,
        usage=usage,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-g', '--gatherer', dest='gatherer', action='store_true',
        help='Start a Gatherer collecting tweets based on filters passed with -f (--filters)'
    )
    parser.add_argument(
        '-f', '--filters', dest='filters', nargs='+',
        help='Text to filter a gatherer on e.g. "Victuals" "Delicious"\n(Note: filters are case insensitive)'
    )
    parser.add_argument(
        '-c', '--chef', dest='chef', action='store_true',
        help='Start a Chef transforming raw tweets piped in into delicious tweets'
    )
    parser.add_argument(
        '-w', '--waiter', dest='waiter', action='store_true',
        help='Start a Waiter collecting the tweets from the chef, used with either -m (--menu), or -s (--serve) and -t (--table)'
    )
    parser.add_argument(
        '-m', '--menu', dest='menu', action='store_true',
        help='Return a list of items available from the chef'
    )
    parser.add_argument(
        '-o', '--order', dest='order', nargs='+', metavar='ITEM',
        help='The item(s) to serve, provided in order of precedence, will serve an nested json'
    )
    parser.add_argument(
        '-s', '--serve', dest='serve', nargs='*', metavar='ITEM',
        help='The item(s) to serve'
    )
    parser.add_argument(
        '-t', '--table', dest='table', nargs='?',
        help='The location to deliver the items to (output is an sqlite database), if no location is provided will attempt default to values in config'
    )
    args = parser.parse_args()

    # See what we need to do
    if args.gatherer:
        if args.filters:
            gatherer = Gatherer(args.filters)
            gatherer.gather()
    elif args.chef:
        chef = Chef()
        chef.cook()
    elif args.waiter:
        waiter = Waiter()
        if args.menu:
            waiter.menu()
        elif args.order:
            waiter.order(args.order)
        else:
            waiter.serve(args.serve, args.table)
    else:
        parser.print_help()

    sys.exit(0)

if __name__ == '__main__':
    main()
