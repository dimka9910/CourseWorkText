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




def main():
    generation = TextGeneration()
    generation.run()


if __name__ == '__main__':
    main()
