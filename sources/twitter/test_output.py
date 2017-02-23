# -*- coding: utf-8 -*-
"""
Twitter stream output test

Make sure the output file works ok.
Note: built to work on output locations defined in config

@category   Utility
@version    $ID: 0.1.1, 2016-12-05 17:00:00 CST $;
@author     KMR
@licence    MIT (X11)
"""
import os, yaml
import pandas as pd
from datetime import datetime
from matplotlib import pyplot

#Load in the config
dir = os.path.dirname(os.path.realpath(__file__))
conf = yaml.safe_load(open("{}/twitter.cfg".format(dir)))

in_file = datetime.now().strftime(conf['out_loc'].format(dir))
df = pd.DataFrame.from_csv(in_file, sep='\t', encoding='utf-8')

#Analyzing by platform
print('Analyzing tweets by platform\n')
tweets_by_source = df['source'].value_counts()
print("{}".format(tweets_by_source))
fig, ax = pyplot.subplots()
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Source', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Top 10 platforms', fontsize=15, fontweight='bold')
tweets_by_source[:10].plot(ax=ax, kind='bar', color='red')
pyplot.tight_layout()
pyplot.show()

#Analyzing by Language
print('Analyzing tweets by language\n')
tweets_by_lang = df['language'].value_counts()
print("{}".format(tweets_by_lang))
fig, ax = pyplot.subplots()
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Source', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Top 10 platforms', fontsize=15, fontweight='bold')
tweets_by_lang[:10].plot(ax=ax, kind='bar', color='red')
pyplot.tight_layout()
pyplot.show()

#Analyzing by Language
print('Analyzing tweets by time zone\n')
user_time_zones = df['user_time_zone'].value_counts()
print("{}".format(user_time_zones))
fig, ax = pyplot.subplots()
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Source', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Top 10 platforms', fontsize=15, fontweight='bold')
user_time_zones[:10].plot(ax=ax, kind='bar', color='red')
pyplot.tight_layout()
pyplot.show()