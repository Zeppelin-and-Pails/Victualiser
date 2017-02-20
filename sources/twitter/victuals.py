# -*- coding: utf-8 -*-
"""
Twitter stream

For use with victualiser, handles twitter streams.

@category   Utility
@version    $ID: 0.1.1, 2016-12-05 17:00:00 CST $;
@author     KMR
@licence    MIT (X11)
"""
import re, json
import os, yaml
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as pyplot
from textblob import TextBlob
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

class TwitterStreamListener(StreamListener):
    def __init__(self, api=None, file_path='data.json', limit=1, limit_type='count'):
        # Use the api provided or try a generic one
        self.api = api or API()
        # Try to open the output file
        try:
            self.out = open(file_path, 'w', encoding="utf-8")
        except Exception as e:
            raise e
        # Setup the other pieces needed to run nicely
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
                    self.out.close()
                    return False

            # Write the data out
            self.out.write("{}\n".format(json.dumps(status._json)))

            # Check if we've reached a count limit
            if self.ltype == 'count':
                self.counter += 1
                if self.counter >= self.limit:
                    self.out.close()
                    return False
            return True

        except Exception as e:
            print('Failed on_status: ', str(e))
            pass

    def on_error(self, status):
        # See if we're rate limited, if not just keep on going
        if status == 420:
            return False
        print(status)
        return True

class Gatherer:
    def __init__(self, filters):
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
        # Build the output path and make sure the parent dirs are there
        file_path = datetime.now().strftime(
            "{}/{}".format( self.conf['data_dir'].format(self.dir),
                            self.conf['out_file'] )
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Initialise and configure the stream listener
        sl = TwitterStreamListener(API(self.auth), file_path, self.conf['limit_count'], self.conf['limit_type'])
        self.stream = Stream(auth=self.auth, listener=sl)
        self.stream.filter(track=self.filters)

        # Give the caller back the location of all our victuals
        return file_path

class Chef:
    def __init__(self, in_path, out_path):
        """
        Initialise a new chef to enrich the data

        :param path: the path to a file containing raw tweets in stringified json form
        """
        self.in_path = in_path
        self.out_path = out_path

        self.source_re = re.compile('>(.+)</a>')

        # Make sure the output dirs are there and try to open the file
        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)

    def cook(self):
        """
        Make the data delicious
        :return: path: the output path for the file with all the nice new data
        """
        # Open the output file, if we can't somethings wrong
        try:
            out_file = open(self.out_path, 'w', encoding="utf-8")
        except Exception as e:
            raise e

        # Open the input file and read through the lines
        with open(self.in_path, 'r', encoding="utf-8") as f:
            for line in f:
                # Load the JSON and build a TextBlob for some nice text analytics
                tweet = json.loads(line)
                blob = TextBlob(tweet['text'])
                m = self.source_re.search(tweet['source'])

                tweet_data = {
                    'text': tweet['text'],
                    'created_at': tweet['text'],
                    'source': m.group(1),
                    'source_full': tweet['source'],
                    'retweets': tweet['retweet_count'],
                    'favorites': tweet['favorite_count'],
                    'coordinates': tweet['coordinates'],
                    'language': tweet['lang'],
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity,
                    'noun_phrases': blob.noun_phrases,
                    'user':{
                        'location': tweet['user']['location'],
                        'time_zone': tweet['user']['time_zone'],
                        'user_lang': tweet['user']['lang'],
                        'friends': tweet['user']['friends_count'],
                        'followers': tweet['user']['followers_count'],
                        'statuses': tweet['user']['statuses_count'],
                        'favourites': tweet['user']['favourites_count'],
                        'listed': tweet['user']['listed_count'],
                        'verified': tweet['user']['lang'],
                    }
                }
                if tweet['place']:
                    tweet_data['place'] = {
                        'place_type': tweet['place']['place_type'],
                        'full_name': tweet['place']['full_name'],
                        'country': tweet['place']['country'],
                    }
                # Write out the new data
                out_file.write("{}\n".format(json.dumps(tweet_data, sort_keys=True)))

        return self.out_path

class Waiter:
    def __init__(self, in_path):
        """
        Initialise a new waiter to serve our completed data

        :param path: the path to a file containing cooked tweets in stringified json form
        """
        self.in_path = in_path

    def serve(self, items=None):
        """
        Serve up the cooked data
        :param items - optional: a list of items to return, if not passed will return the full dataframe
        :return: pandas.DataFrame containing data loaded from the in_path
        """
        tweets = []
        # Open the input file and load the json into a list
        with open(self.in_path, 'r', encoding="utf-8") as f:
            for line in f:
                tweets.append(json.loads(line))

        # Use pandas' nice json_normalize function to flatten the structure and map the columns
        tweets_frame = pd.io.json.json_normalize(tweets, record_prefix=True)
        tweets_frame.columns = tweets_frame.columns.map(lambda x: x.split(".")[-1])

        # If we have a filter of items apply that and return the frame
        if isinstance(items, list):
            return tweets_frame.loc[:, items]
        return tweets_frame

if __name__ == '__main__':

    gatherer = Gatherer(['delicious'])
    larder = gatherer.gather()

    chef = Chef(larder, re.sub(r"\.json$", "_processed.json", larder))
    meals = chef.cook()

    waiter = Waiter(meals)
    meal = waiter.serve(
        ['text','language','source','country']
    )

    #Analyzing Tweets by Language
    print('Analyzing tweets by platform\n')
    tweets_by_lang = meal['source'].value_counts()
    fig, ax = pyplot.subplots()
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.set_xlabel('Source', fontsize=15)
    ax.set_ylabel('Number of tweets' , fontsize=15)
    ax.set_title('Top 10 platforms', fontsize=15, fontweight='bold')
    tweets_by_lang[:10].plot(ax=ax, kind='bar', color='red')
    pyplot.tight_layout()
    pyplot.show()

