# coding=utf-8

import blvd_text
import time
import tagRpc_pb2

from libshorttext.analyzer import *
from libshorttext.classifier import *
from functools import partial

import logging
import traceback

logging.basicConfig()

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

analyzer = Analyzer('outputs/16.2.1-2.model')


class TagRpc(tagRpc_pb2.BetaTagRpcServicer):
    @staticmethod
    def classify(reply, _message):
        message = _message.encode('utf8')
        tokens, indices, word_list = blvd_text.tokenize_with_indices(message)
        message = ' '.join(tokens)
        prediction_res = predict_single_text(str(message), analyzer.model)
        decvals = prediction_res.decvals
        features, weights, labels = analyzer.model.get_weight(str(message))

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

            reply.results.add(relWord=word, tag=label)
        else:
            reply.results.add(tag='skipped')

    def ClassifyBulk(self, request, context):
        try:
            reply = tagRpc_pb2.TagRpcReply()
            classify = partial(self.classify, reply)
            map(classify, request.messages)
            return reply
        except Exception as e:
            print(traceback.format_exc())
            # this is taken from https://github.com/grpc/grpc/issues/3436;
            # however, it does not seem to work.
            context.details('An exception with message "%s" was raised!', e.message)
            context.code(tagRpc_pb2.beta_interfaces.StatusCode.INTERNAL)
            return tagRpc_pb2.TagRpcReply()


server = tagRpc_pb2.beta_create_TagRpc_server(TagRpc())
server.add_insecure_port('[::]:4241')
server.start()

try:
    while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
except KeyboardInterrupt:
    server.stop(0)
