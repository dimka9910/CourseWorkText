import argparse
import logging
import os
import sys

import pandas as pd
from fastai.text import TextLMDataBunch, URLs, language_model_learner, csv, AWD_LSTM, Transformer, load_learner, Path
from sklearn.model_selection import train_test_split

logger = logging.getLogger()
logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

def str2bool(v):
    """Convert a string to a bool, this makes sure argument parsing goes right,
     based on https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_args():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='Script to generate tweets')
    parser.add_argument('--job_id', '-j', metavar='STRING', default="gosha-group",
                        help="Job_id used for opening and saving files")
    parser.add_argument('--data', '-d', metavar='STRING', default='./vk-parsed/',
                        help="The CSV with the tweets")
    parser.add_argument('--model_path', '-mp', metavar='STRING', default=os.path.join(os.getcwd(), 'model/'),
                        help="Where the model is or should be stored")
    parser.add_argument("--train", '-t', type=str2bool, nargs='?', const=True, default=False,
                        help="Do we need to train a model?")
    parser.add_argument('--use_pretrained', '-p', metavar='BOOL', default=True,
                        help="Do we use a pretrained model?")
    parser.add_argument('--n_tweets', '-n', metavar='STRING', default=10,
                        help="How many tweets to generate")
    parser.add_argument('--n_words', '-w', metavar='STRING', default=300,
                        help="How many words should be generated at a time")
    parser.add_argument('--architecture', '-a', metavar='STRING', default='AWD_LSTM',
                        help='Which architecture do we want to use?')
    parser.add_argument('--epochs', '-e', metavar='INT',
                        default=10, help='Amount of epochs in training')
    return parser.parse_args()


class TextGeneration:
    def __init__(self):
        # Here we init stuff
        self.args = get_args()
        self.trained = not bool(self.args.train)

        self.dropout = 0.5
        self.epochs = int(self.args.epochs)
        self.batch_size = 32

        self.train_df = None
        self.validation_df = None
        self.test_df = None
        self.model = None
        self.data_lm = None
        logger.info(self.args)

        # Make sure the path for saving the model exists
        if not os.path.exists(self.args.model_path):
            os.makedirs(self.args.model_path)

    @staticmethod
    def prettify_tweet(tweet):
        """Prettifies tweet by removing spaces around some tokens, mostly interpunction"""

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

    def generate(self, count=10, max_words=280):
        """Generates new tweets with the language model"""
        logger.info("Generating tweets")
        generated_tweets = []

        # Generate text until we have enough tweets
        while len(generated_tweets) < count:
            # Generate text
            raw_generated = self.model.predict("xxbos", n_words=max_words, temperature=0.8)

            # Split on begin of sentence token
            raw_tweets = raw_generated.split("xxbos ")[1:]

            # Iterate through tweets, prettify the tweets and save the tweets
            for tweet in raw_tweets[:-1]:  # Skip last xxbos as it is 99% chance it is an incomplete tweet
                tweet = self.prettify_tweet(tweet)
                if tweet and len(tweet) <= 280:
                    generated_tweets.append(tweet)
        return generated_tweets

    def run(self):
        """Main part of program, handles all the different steps"""
        if self.args.train:
            self.load_data()

            logger.info("Start training the model")
            # self.train(epochs=3, batch_size=32)
            self.train(epochs=self.epochs, batch_size=64)

            logger.info("Start testing")
            self.test()

            if self.args.job_id == "":
                model_name = "no_name.pkl"
            else:
                model_name = str(self.args.job_id) + ".pkl"
            self.model.export(Path(os.path.join(self.args.model_path, model_name)))
        else:
            logger.info("Loading a pretrained model")
            self.model = load_learner(Path(self.args.model_path), self.args.job_id + '.pkl')
        generated_tweets = self.generate(int(self.args.n_tweets), int(self.args.n_words))
        for tweet in generated_tweets:
            print("Tweet:\n" + tweet)


def main():
    generation = TextGeneration()
    generation.run()


if __name__ == '__main__':
    main()