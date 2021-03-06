import os

import tensorflow as tf

from train import train
from evaluate import evaluate
from data_structure import load_data

flags = tf.app.flags

flags.DEFINE_string('gpu', '0', 'visible gpu')

flags.DEFINE_string('mode', 'eval', 'set train or eval')

flags.DEFINE_string('datadir', 'data', 'directory of input data')
flags.DEFINE_string('dataname', 'appliances.pkl', 'name of data')
flags.DEFINE_string('modeldir', 'model', 'directory of model')
flags.DEFINE_string('modelname', 'appliances', 'name of model')

flags.DEFINE_bool('discourserank', True, 'flag of discourserank')
flags.DEFINE_float('damp', 0.9, 'damping factor of discourserank')

flags.DEFINE_integer('epochs', 10, 'epochs')
flags.DEFINE_integer('batch_size', 8, 'batch size')
flags.DEFINE_integer('log_period', 500, 'valid period')

flags.DEFINE_string('opt', 'Adagrad', 'optimizer')
flags.DEFINE_float('lr', 0.1, 'lr')
flags.DEFINE_float('norm', 1e-4, 'norm')
flags.DEFINE_float('grad_clip', 10.0, 'grad_clip')
flags.DEFINE_float('keep_prob', 0.95, 'keep_prob')
flags.DEFINE_integer('beam_width', 10, 'beam_width')
flags.DEFINE_float('length_penalty_weight', 0.0, 'length_penalty_weight')

flags.DEFINE_integer('dim_hidden', 256, 'dim_output')
flags.DEFINE_integer('dim_str', 128, 'dim_output')
flags.DEFINE_integer('dim_sent', 384, 'dim_sent')

# for evaluation
flags.DEFINE_string('refdir', 'ref', 'refdir')
flags.DEFINE_string('outdir', 'out', 'outdir')

# special tokens
PAD = '<pad>' # This has a vocab id, which is used to pad the encoder input, decoder input and target sequence
UNK = '<unk>' # This has a vocab id, which is used to represent out-of-vocabulary words
BOS = '<p>' # This has a vocab id, which is used at the beginning of every decoder input sequence
EOS = '</p>' # This has a vocab id, which is used at the end of untruncated target sequences

def main(_):
    config = flags.FLAGS
    print(str(config.flag_values_dict()))
    
    os.environ['CUDA_VISIBLE_DEVICES'] = config.gpu

    print('loading data...')
    train_batches, dev_batches, test_batches, embedding_matrix, vocab, word_to_id  = load_data(config)
    
    flags.DEFINE_integer('PAD_IDX', word_to_id[PAD], 'PAD_IDX')
    flags.DEFINE_integer('UNK_IDX', word_to_id[UNK], 'UNK_IDX')
    flags.DEFINE_integer('BOS_IDX', word_to_id[BOS], 'BOS_IDX')
    flags.DEFINE_integer('EOS_IDX', word_to_id[EOS], 'EOS_IDX')
    
    n_embed, d_embed = embedding_matrix.shape
    flags.DEFINE_integer('n_embed', n_embed, 'n_embed')
    flags.DEFINE_integer('d_embed', d_embed, 'd_embed')

    maximum_iterations = max([max([d._max_sent_len(None) for d in batch]) for ct, batch in dev_batches])
    flags.DEFINE_integer('maximum_iterations', maximum_iterations, 'maximum_iterations')    
    
    if config.mode == 'train':
        train(config, train_batches, dev_batches, test_batches, embedding_matrix, vocab)
    elif config.mode == 'eval':
        evaluate(config, test_batches, vocab)

if __name__ == "__main__":
    tf.app.run()
    
    
    