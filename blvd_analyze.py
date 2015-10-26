# coding=utf-8

import blvd_text
import json

from libshorttext.analyzer import *
from libshorttext.classifier import *

analyzer = Analyzer('outputs/15.10.26.model')

import zerorpc

import logging
logging.basicConfig()


class BlvdAnalyzer():

    def __init__(self):
        self.is_currently_useless = True

    @staticmethod
    def run(text):
        tokens, indices, word_list = blvd_text.tokenize_with_indices(text)
        text = ' '.join(tokens)
        prediction_res = predict_single_text(str(text), analyzer.model)
        decvals = prediction_res.decvals
        features, weights, labels = analyzer.model.get_weight(str(text))

        max_decval = max(decvals)
        idx = decvals.index(max_decval)
        label = labels[idx]

        if max_decval <= 0:
            decvals[idx] = 0.1e-10  # hacking the way out of divide by zero problem.

        # if label == 'skipped':
        #     skipped_decval = decvals[idx]
        #     nb_decval = max(decvals[:idx] + decvals[idx+1:])  # nb = 'next best'
        #     nb_idx = decvals.index(nb_decval)
        #     ratio = nb_decval / skipped_decval
        #     if ratio > 0.2:
        #         idx = nb_idx
        #         label = labels[idx]

        label_weights = []
        # probably maps or something clever
        for weight in weights:
            label_weights.append(weight[idx])
        if label_weights:
            feature_idx = label_weights.index(max(label_weights))
            feature = features[feature_idx]
            token_idx = None
            try:
                token_idx = tokens.index(feature)
            except ValueError:
                for token in tokens:
                    if feature[0] in token:
                        token_idx = tokens.index(token)

            word_idx = indices[token_idx]
            word = word_list[word_idx]

            return json.dumps({'relWord': word, 'tag': label})
        else:
            return json.dumps({'relWord': None, 'tag': 'skipped'})

s = zerorpc.Server(BlvdAnalyzer(), heartbeat=None)
s.bind('tcp://0.0.0.0:4241')
s.run()
