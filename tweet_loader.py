#!/usr/bin/env python
# encoding: utf-8

import tweepy  # https://github.com/tweepy/tweepy
import json
import sys

# Twitter API credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=199)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=199, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

    # print total tweets fetched from given screen name
    print
    "Total tweets downloaded from %s are %s" % (screen_name, len(alltweets))

    return alltweets


def fetch_tweets(screen_names):
    # initialize the list to hold all tweets from all users
    alltweets = []

    # get all tweets for each screen name
    for screen_name in screen_names:
        alltweets.extend(get_all_tweets(screen_name))

    return alltweets


def store_tweets(alltweets, file='tweets.json'):
    # a list of all formatted tweets
    tweet_list = []

    for tweet in alltweets:
        # a dict to contain information about single tweet
        tweet_information = dict()

        # text of tweet
        tweet_information['text'] = tweet.text.encode('utf-8')

        # date and time at which tweet was created
        tweet_information['created_at'] = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")

        # id of this tweet
        tweet_information['id_str'] = tweet.id_str

        # retweet count
        tweet_information['retweet_count'] = tweet.retweet_count

        # favourites count
        tweet_information['favorite_count'] = tweet.favorite_count

        # screename of the user to which it was replied (is Nullable)
        tweet_information['in_reply_to_screen_name'] = tweet.in_reply_to_screen_name

        # user information in user dictionery
        user_dictionery = tweet._json['user']

        # no of followers of the user
        tweet_information['followers_count'] = user_dictionery['followers_count']

        # screename of the person who tweeted this
        tweet_information['screen_name'] = user_dictionery['screen_name']

        # add this tweet to the tweet_list
        tweet_list.append(tweet_information)

    # open file desc to output file with write permissions
    file_des = open(file, 'wb')

    # dump tweets to the file
    json.dump(tweet_list, file_des, indent=4, sort_keys=True)

    # close the file_des
    file_des.close()


if __name__ == '__main__':

    # pass in the username of the account you want to download
    alltweets = get_all_tweets("Rogozin")

    # store the data into json file
    if len(sys.argv[2]) > 0:
        store_tweets(alltweets, "./outpu")
    else:
        store_tweets(alltweets)