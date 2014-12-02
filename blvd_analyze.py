# coding=utf-8

import blvd_text
import json

from libshorttext.analyzer import *
from libshorttext.classifier import *

analyzer = Analyzer('outputs/0.0.3.model')

import zerorpc

import logging
logging.basicConfig()


class BlvdAnalyzer():

    def __init__(self, text):
        self.tokens, self.indices, self.word_list = blvd_text.tokenize_with_indices(text)
        text = ' '.join(self.tokens)

        prediction_res = predict_single_text(str(text), analyzer.model)
        self.decvals = prediction_res.decvals

        self.features, self.weights, self.labels = analyzer.model.get_weight(str(text))

        positives = [i for i in self.decvals if i > 0]

        if positives:
            self.result_data = map(self.map_result_data, positives)
            sorted(self.result_data, cmp=lambda x, y: cmp(x['weight'], y['weight']))

            skipped = [i for i in self.result_data if i['label'] == 'skipped']

            if skipped:
                self.handle_skipped(skipped)

        else:
            self.result_data = 'skipped'

    def map_result_data(self, decval):
        label_weights = []
        idx = self.decvals.index(decval)
        label = self.labels[idx]

        for weight in self.weights:
            label_weights.append(weight[idx])

        if label_weights:
            max_weight = max(label_weights)
            feature_idx = label_weights.index(max_weight)
            feature = self.features[feature_idx]

            token_idx = None
            try:
                token_idx = self.tokens.index(feature)
            except ValueError:
                for token in self.tokens:
                    if feature[0] in token:
                        token_idx = self.tokens.index(token)
            if token_idx is None:
                raise Exception("Can't find token.")

            word_idx = self.indices[token_idx]
            word = self.word_list[word_idx]

            return {
                'word': word,
                'label': label,
                'weight': max_weight,
            }
        else:
            raise Exception("No label weights?")

    def handle_skipped(self, skipped):
        idx = self.result_data.index(skipped[0])
        if len(self.result_data) < 2:
            self.result_data = 'skipped'
        elif idx > 0:
            del self.result_data[idx]
        else:
            skip_idx = self.labels.index('skipped')
            skip_decval = self.decvals[skip_idx]
            nb_idx = self.labels.index(self.result_data[1]['label'])
            nb_decval = self.decvals[nb_idx]
            ratio = nb_decval / skip_decval
            if ratio > 0.2:
                del self.result_data[0]
            else:
                self.result_data = 'skipped'

    def check_dupes(self):
        for x in self.result_data:
            for idx, y in enumerate(self.result_data):
                if x['word'] == y['word'] and x['weight'] > y['weight']:
                    del self.result_data[idx]


class Interface():

    @staticmethod
    def classify(text):
        analysis = BlvdAnalyzer(text)
        return json.dumps(analysis.result_data)

s = zerorpc.Server(Interface())
s.bind('tcp://0.0.0.0:4241')
s.run()
