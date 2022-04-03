# -*- coding: utf-8 -*-
import config
import telebot
import time
import utils
import parser
from telebot import types
import argparse
import logging
import os
import sys

import pandas as pd
from fastai.text import TextLMDataBunch, URLs, language_model_learner, csv, AWD_LSTM, Transformer, load_learner, Path
from sklearn.model_selection import train_test_split

bot = telebot.TeleBot(config.token)
logger = logging.getLogger()


@bot.message_handler(commands=['start'])
def start(message):
    logger.info("start")
    try:
        text = "1) alina \n 2) gosha \n 3) dima"
        markup = utils.generate_markup(3)
        bot.send_message(message.chat.id, text, reply_markup=markup)
    except Exception:
        pass

def prettify_tweet(tweet):
    # Set up character sets
    no_leading_space = ['?', '!', ',', '.', '\'', '’', '”', 'n\'t', 'n’t', '%', ')', ':']
    no_trailing_space = ['$', '#', '“', '(']

    # Remove space in front of characters
    for char in no_leading_space:
        tweet = tweet.replace(' ' + char, char)

    # Remove space after characters
    for char in no_trailing_space:
        tweet = tweet.replace(char + ' ', char)
    return tweet



@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    try:
        if message.text == "/start":
            start(message)
            return

        text = message.text

        model = load_learner(Path(os.path.join(os.getcwd(), 'model/')), text + '.pkl')
        generated_tweets = 0
        # Generate text until we have enough tweets
        while generated_tweets < 10:
            logger.info(generated_tweets)
            # Generate text
            raw_generated = model.predict("xxbos", n_words=280, temperature=0.8)
            # Split on begin of sentence token
            raw_tweets = raw_generated.split("xxbos ")[1:]
            # Iterate through tweets, prettify the tweets and save the tweets
            for tweet in raw_tweets[:-1]:  # Skip last xxbos as it is 99% chance it is an incomplete tweet
                tweet = prettify_tweet(tweet)
                if tweet and 280 >= len(tweet) > 10:
                    logger.info(tweet)
                    generated_tweets += 1
                    bot.send_message(message.chat.id, tweet)
    except Exception:
        bot.send_message(message.chat.id, "МОДЕЛЬ НЕ НАЙДЕНА")


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(1)
        print(e)
        pass
