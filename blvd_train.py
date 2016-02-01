from libshorttext.classifier import *
from blvd_text import process as process_text


def make_path(f_name, ext):
    return './outputs/' + f_name + '.' + ext


def train(name, svm_path=None, converter=None):
    if not svm_path:
        svm_path = make_path(name, 'svm')
    if not converter:
        converter = Text2svmConverter().load(make_path(name, 'text_converter'))
    model = train_converted_text(svm_path, converter, feature_arguments='-T 1 -I 1')
    model.save(make_path(name, 'model'), True)


def convert_and_train(name, source):
    svm_path = make_path(name, 'svm')
    converter_path = make_path(name, 'text_converter')
    converter = process_text(source, svm_path, converter_path)
    train(name, svm_path, converter)

# ex
# convert_and_train('16.2.1-2', './training_data/post_1454335047804');
