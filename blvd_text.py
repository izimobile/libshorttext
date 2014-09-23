from libshorttext.converter import *

import re
import unicodedata


def trim_links(input_text):
    input_text = re.sub(r' (http|www|t\.co).*?(?: |$)', '', input_text)
    return input_text


def trim_char(c):
    if ord(c) > 127:
        return ''
    if c.isdigit() or c.isalpha() or c.isspace():
        return c
    if re.match(r'[#\$%/\-_]', c):
        return c
    else:
        return ''


def trim_hashtags(input_text):
    tag = re.search(r'#+([\w_]+[\w\'_\-]*[\w_]+)', input_text)
    if tag:
        hashtag = tag.group(0)
        tag_text = tag.group(1)
        splittable = re.match(r'.*([A-Z]|_|-|\d)', tag_text)
        if splittable:
            tokens = [token for token in re.split(r'([A-Z][a-z]*)|_|-|(\d*)', tag_text) if token]
            new_text = ' '.join(tokens)
            input_text = input_text.replace(hashtag, new_text)
            return trim_hashtags(input_text)
        else:
            input_text = input_text.replace(hashtag, tag_text)
            return trim_hashtags(input_text)
    else:
        return input_text


def trim_spaces(input_text):
    return re.sub(r'\s+', r' ', input_text)


def replace_special(input_text):
    input_text = re.sub(r'\d+', r'number', input_text)
    input_text = re.sub(r'\$', r'dolsign', input_text)
    input_text = re.sub(r'%', r'percent', input_text)
    return re.sub(r'/', r'slash', input_text)


def make_tokens(text):
    text = unicodedata.normalize('NFD', unicode(text, 'utf-8'))
    text = trim_links(text)
    text = ''.join(map(trim_char, text))
    text = trim_hashtags(text)
    text = re.sub(r'([a-z])([0-9])', r'\1 \2', text)
    text = re.sub(r'([0-9])([a-z])', r'\1 \2', text)
    text = trim_spaces(text)
    text = replace_special(text)
    return text


def tokenize(text):
    text = make_tokens(text)
    return text.lower().split()


def tokenize_with_indices(text):
    tokens = []
    indices = []
    word_list = []
    words = text.split()

    for word in words:
        try:
            index = word_list.index(word)
        except ValueError:
            word_list.append(word)
            index = len(word_list) - 1

        word = make_tokens(word)
        word_tokens = word.split()

        for token in word_tokens:
            tokens.append(token.lower())
            indices.append(index)

    return tokens, indices, word_list


def process(source, svm_out, convert_out=None):
    import os
    os.chdir(os.path.dirname(__file__))
    text_converter = Text2svmConverter('-stopword 1 -stemming 1')
    text_converter.text_prep.tokenizer = tokenize
    convert_text(source, text_converter, svm_out)
    if convert_out:
        text_converter.save(convert_out)

# process('training_data/post_sale,event,food,info,hours,skipped',
#         'outputs/test1.svm',
#         'outputs/test1.text_converter')
