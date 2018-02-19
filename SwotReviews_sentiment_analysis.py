# -*- coding: utf-8 -*-
"""
SWOTReviews_sentiment_analysis
~~~~~~~~~~~~~~~~~~~~~~~~
Name: Siraj Munir
Program that show user sentiments while giving reviews for different restuarants (Mgative or Positive).
Positive= 1.0 | >1.0
Negative= -1.0 | < -1.0
In case of positive sentiments, It will give 4 stars for 1.0 and 5 for > 1.0
In case of Negatice sentiments, It will give 2 stars for -1.0 and 1 for < -1.0 i.e: -2.0 or less
In case of Neutral sentiments, It will give 3 stars for 0.0
Rating will be shown at the end of sentiment analysis

"""

from pprint import pprint
import nltk
import yaml
import pandas as pd

import csv
import sys
import os
import re

class Splitter(object):

    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):

    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

class DictionaryTagger(object):

    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

def value_of(sentiment):
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0

def sentence_score(sentence_tokens, previous_token, acum_score):    
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
            elif 'dec' in previous_tags:
                token_score /= 2.0
            elif 'inv' in previous_tags:
                token_score *= -1.0
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])

if __name__ == "__main__":
    #trying to take input from txt or csv file
    """
    text = open('foodreviews.csv', 'r')
    reader = csv.reader(text)
    new_rows_list = []
    for row in reader:
        if row[4] == 'text':
            new_row = [row[5], 'score']
            new_rows_list.append(new_row)
            #text=text
            text.close()

    userinput = input('Enter the filname:')
    myfile= open(userinput)
    text= myfile.readline()
    print (text)
    myfile.close()
"""
#    df1 = pd.read_csv("foodreviews.csv")
 #   print(df1)
    df1 = pd.read_csv("foodreviews.csv")
    for i in df1['sentence']:
        print(i)
        text = i
        print(text)
    #text= input("Enter the food review: ") #yahan se input lega file se
    #print(text)
   # text = """Went to Pizza Hut(North Nazimabad) with family and had the worst service ever. We sat there for approx 10 mins waiting for someone to give us the menu and then when we finally got the menu, there's no one to take our menu. We didn't even get forks and knives until we asked for them. Pizza Hut should hire more TRAINED staff members to provide a satisfactory service to their customers."""

        splitter = Splitter()
        postagger = POSTagger()
        dicttagger = DictionaryTagger([ 'dicts/positive.yml', 'dicts/negative.yml', 
                                        'dicts/inc.yml', 'dicts/dec.yml', 'dicts/inv.yml'])

        splitted_sentences = splitter.split(text)
        pprint(splitted_sentences)

        pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
        pprint(pos_tagged_sentences)

        dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)
        pprint(dict_tagged_sentences)

    #Scores= negative or positive?
        print("analyzing sentiment...")
        score = sentiment_score(dict_tagged_sentences)
        print(score) #yeh cheez usi file mei print hojaye

        #Rating
        if score == 1.0:
            print("4 Stars")
        elif score > 1.0:
            print("5 Stars")
        elif score == -1.0:
            print("2 Stars")
        elif score < -1.0:
            print("1 Star")
        else:
            print("3 Stars")

