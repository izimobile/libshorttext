import blvd_text
import json

from libshorttext.analyzer import *
from libshorttext.classifier import *

analyzer = Analyzer('outputs/test1.model')


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

        idx = decvals.index(max(decvals))
        label = labels[idx]
        label_weights = []
        # probably maps or something clever
        for weight in weights:
            label_weights.append(weight[idx])
        feature_idx = label_weights.index(max(label_weights))
        feature = features[feature_idx]
        try:
            token_idx = tokens.index(feature)
        except ValueError:
            for token in tokens:
                if feature[0] in token:
                    token_idx = tokens.index(token)

        word_idx = indices[token_idx]
        word = word_list[word_idx]

        return json.dumps({'relWord': word, 'tag': label})

import zerorpc

s = zerorpc.Server(BlvdAnalyzer())
s.bind('tcp://0.0.0.0:4241')
s.run()
