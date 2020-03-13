# coding:utf-8

import gzip
import json
import os
import re

import pandas as pd
import tensorflow as tf
from nltk.tokenize import word_tokenize

import _pickle as cPickle

import numpy as np

flags = tf.app.flags

flags.DEFINE_string('input_path', 'data/Appliances_5.json.gz', 'path of output data')
flags.DEFINE_string('output_path', 'data/appliances_df.pkl', 'path of output data')

flags.DEFINE_integer('min_doc_l_train', 10, 'minimum length of document for training')
flags.DEFINE_integer('max_doc_l_train', 60, 'maximum length of document for training')
flags.DEFINE_integer('max_sent_l_train', 50, 'maximum length of sentence for training')

flags.DEFINE_integer('min_doc_l_test', 5, 'minimum length of document for evaluation')
flags.DEFINE_integer('max_doc_l_test', 60, 'maximum length of document for evaluation')
flags.DEFINE_integer('max_sent_l_test', 50, 'maximum length of sentence for evaluation')

# def get_df(path):
#     def parse(path):
#         g = gzip.open(path, 'rb')
#         for l in g:
#             yield eval(l)
#     i = 0
#     df = {}
#     for d in parse(path):
#         df[i] = d
#         i += 1
#     return pd.DataFrame.from_dict(df, orient='index')

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def get_df(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

def get_tokens(doc):
    shortened = {
    '\'m': ' am',
    '\'re': ' are',
    '\'ll': ' will',
    '\'ve': ' have',
    'it\'s': 'it is',
    'isn\'t': 'is not',
    'aren\'t': 'are not',
    'wasn\'t': 'was　not',
    'weren\'t': 'were　not',
    'don\'t': 'do　not',
    'doesn\'t': 'does　not',
    'didn\'t': 'did　not',
    'haven\'t': 'have　not',
    'hasn\'t': 'has　not',
    'hadn\'t': 'had　not',
    'can\'t': 'can　not',
    'couldn\'t': 'could　not',
    'won\'t': 'will　not',
    'wouldn\'t': 'would　not',
    'cannot': 'can　not',
    'wanna': 'want to',
    'gonna': 'going to',
    'gotta': 'got to',
    'hafta': 'have to',
    'needa': 'need to',
    'outta': 'out of',
    'kinda': 'kind of',
    'sorta': 'sort of',
    'lotta': 'lot of',
    'lemme': 'let me',
    'gimme': 'give me',
    'getcha': 'get you',
    'gotcha': 'got you',
    'letcha': 'let you',
    'betcha': 'bet you',
    'shoulda': 'should have',
    'coulda': 'could have',
    'woulda': 'would have',
    'musta': 'must have',
    'mighta': 'might have',
    'dunno': 'do not know',
    }
    
    doc = doc.lower()
    shortened_re = re.compile('(?:' + '|'.join(map(lambda x: '\\b' + x + '\\b', shortened.keys())) + ')')
    doc = shortened_re.sub(lambda x: shortened[x.group(0)], doc)
    
    doc = re.sub(r"\(.*?\)", "",doc)
    doc = re.sub(r"!", ".",doc)
    sents = [re.sub(r"[^A-Za-z0-9()\'\`_/]", " ", sent).lstrip() for sent in doc.split('.') if sent != '']
    
    tokens = []
    for s in sents:
        s = ' '.join(word_tokenize(s))
        s = s.replace(" n't ", "n 't ")
        s = s.split()
        if len(s) > 1: tokens.append(s)
    return tokens


def parse_amazon():
    config = flags.FLAGS
    print(str(config.flag_values_dict()))

    print('parsing raw data...')
    raw_review_df = get_df(config.input_path)

    review_df = raw_review_df[(raw_review_df['asin'] != '') & (raw_review_df['reviewText'] != '') & (raw_review_df['summary'] != '')]
    reviews = review_df['reviewText'].values
    summaries = review_df['summary'].values
    products = review_df['asin'].values
    ind = np.unravel_index(np.argsort(products, axis=None), products.shape)
    sorted_products = products[ind]
    sorted_reviews = reviews[ind]
    sorted_summaries = summaries[ind]

    pre_product = "pre_product"
    raw_path = "AmazonDataset/raw-copy/"
    gold_path = "AmazonDataset/summaries-gold-copy/"
    raw_file = open(os.path.join(raw_path, pre_product + ".raw"), "w")
    cur_summary_set = set()

    for id, product in enumerate(sorted_products):
        cur_product = product
        if cur_product != pre_product:
            if len(cur_summary_set) != 0:
                result_file = open(os.path.join(gold_path, pre_product + "/" + pre_product + ".gold"), "a")
                for summ in cur_summary_set:
                    result_file.write(summ + "\n")
                result_file.close()
                cur_summary_set = set()

            pre_product = cur_product
            raw_file.close()
            raw_file = open(os.path.join(raw_path, pre_product + ".raw"), "w")

            gold_product_path = os.path.join(gold_path, pre_product)
            if not os.path.isdir(gold_product_path):
                os.mkdir(gold_product_path)


        raw_file.write(sorted_reviews[id] + "\n")
        cur_summary_set.add(sorted_summaries[id])

        # line_num = int(len(sorted_summaries) / 5) + 1
        #
        # for i in range(0, len(sorted_summaries), line_num):
        #     result_file = open(os.path.join(gold_product_path, product + "." + str(i) + ".gold"), "w")
        #     for j in range(i, i + line_num):
        #         if j < len(sorted_summaries):
        #             result_file.write(sorted_summaries[j])
        #             # print(gold[j])
        #     result_file.close()

    print("Done.")

def main():
    config = flags.FLAGS
    print(str(config.flag_values_dict()))
    
    print('parsing raw data...')
    raw_review_df = get_df(config.input_path)
    # raw_review_df = pd.read_json(config.input_path, lines=True)

    review_df = raw_review_df[(raw_review_df['reviewText'] != '') & (raw_review_df['summary'] != '')]
    
    print('splitting text into tokens...')
    review_df['tokens'] = review_df['reviewText'].apply(lambda d: get_tokens(d))
    review_df = review_df[(review_df['tokens'].apply(lambda x: len(x)) > 0)]
    
    review_df['doc_l'] = review_df['tokens'].apply(lambda d: len(d))
    review_df['max_sent_l'] = review_df['tokens'].apply(lambda d: max([len(s) for s in d]))
    review_df['summary_tokens'] = review_df['summary'].apply(lambda s: word_tokenize(s.lower()))
    review_df = review_df[(review_df['summary_tokens'].apply(lambda x: len(x)) > 0)]
    
    print('splitting data into train, dev, test...')
    test_all_df = review_df[0:1000]
    dev_all_df = review_df[1000:2000]
    train_all_df = review_df[2000:]
    
    train_df = train_all_df[(train_all_df['doc_l']>=config.min_doc_l_train)&(train_all_df['doc_l']<=config.max_doc_l_train)&(train_all_df['max_sent_l']<=config.max_sent_l_train)]
    dev_df = dev_all_df[(dev_all_df['doc_l']>=config.min_doc_l_test)&(dev_all_df['doc_l']<=config.max_doc_l_test)&(dev_all_df['max_sent_l']<=config.max_sent_l_test)]
    test_df = test_all_df[(test_all_df['doc_l']>=config.min_doc_l_test)&(test_all_df['doc_l']<=config.max_doc_l_test)&(test_all_df['max_sent_l']<=config.max_sent_l_test)]
    
    print('saving set of train, dev, test...')
    cPickle.dump((train_df, dev_df, test_df), open(config.output_path, 'wb'))
    
if __name__ == "__main__":
    # main()
    parse_amazon()