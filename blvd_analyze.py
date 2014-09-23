import blvd_text

from libshorttext.analyzer import *
from libshorttext.classifier import *

analyzer = Analyzer('outputs/test1.model')


def analyze(text):
    tokens, indices, word_list = blvd_text.tokenize_with_indices(text)
    text = ' '.join(tokens)
    prediction_res = predict_single_text(str(text), analyzer.model)
    decvals = prediction_res.decvals
    features, weights, labels = analyzer.model.get_weight(str(text))
    print 'something'


analyze("OMG biggest sale ever #SaleYourSoul no furreal 98% off don't miss this sale you bastard.")