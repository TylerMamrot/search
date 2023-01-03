from typing import Dict, List, Set

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import everygrams
from nltk import bigrams

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


class Search:
    def __init__(self) -> None:
        self.index: Dict[str:set] = {}  # main dict used to track term and what doc they are listed in
        self.fuzzy: Dict[str:set] = {}  # k gram index to suport fuzzy searching
        self.docs: Dict[int: str]= {}  # contains listing index and stemmed representation of tokens
        self.doc_names: Dict[int: str] = {}  # dict of document index and corresponding document names
        self.doc_number = 0  # tracks number of docs indexed, used to add keys to self.docs
        self.tokenizer = RegexpTokenizer(r'\w+')  # tokenize words only
        self.stemmer = PorterStemmer()  # standard stemmer
        self.min_k_grams = 2
        self.max_k_grams = 2

    def print(self):
        _ = [print(f"{k}: {len(v)}: {v}") for k, v in self.index.items()]

    def _get_kgrams(self):
        _ = [print(f"{k}: {len(v)}: {v}") for k, v in self.k_gram_index.items()]

    def add_document(self, corpus: str, name:str):
        """
        assign index to a document and apply preprocessing, does not reindex engine

        In reality, document would probably be written to disk somewhere
        """
        self.doc_number += 1
        tokens = self.tokenizer.tokenize(corpus)
        filtered_words = [t for t in tokens if t not in stopwords.words('english')]
        stemmed_words = [self.stemmer.stem(w) for w in filtered_words]
        self.docs[self.doc_number] = stemmed_words
        self.doc_names[self.doc_number] = name

    def index_documents(self):
        """
        Indexes each document into inverted index and k gram inverted index
        :return:
        """
        #  empty current index and start from scratch
        self.index = {}
        self.k_gram_index = {}
        for k, document in self.docs.items():
            for token in document:
                if not self.index.get(token):
                    self.index[token] = set()

                grams = bigrams(token)
                for gram in grams:
                    if not self.k_gram_index.get(gram):
                        self.k_gram_index[gram] = set()
                    self.k_gram_index[gram].add(token)

                self.index[token].add(k)


    def get_document_names(self):
        return self.doc_names

    def get(self, key) -> set:
        return self.index.get(key, None)

    def get_kgram(self, key) -> set:
        return self.k_gram_index.get(key, None)

    def update(self, key, listings):
        """
        Manually update a key with listings
        """
        self.delete(key)
        self.index[key] = listings
        return self

    def delete(self, key):
        """
        delete a key from the index
        """
        if self.get(key):
            del self.index[key]
        return self

    def search(self, token, name=False) -> List[str]:
        """
        searches indexes for matching stemm word
        and return list of documents token is found in
        """
        stemmed_token = self.stemmer.stem(token)

        listings = []

        match = self.get(stemmed_token)
        if match:
            listings =[self.doc_names[l] for l in match]
        else:

        # fall back to k gram search if we get no result for the original query
            grams = bigrams(stemmed_token)
            for gram in grams:
                tokens = self.get_kgram(gram)
                if tokens:
                    for t in tokens:
                        stemmed_token = self.stemmer.stem(t)
                        listing = self.get(stemmed_token)
                        token_listings = []
                        if listing:
                            for l in listing:
                                doc = self.doc_names[l]
                                token_listings.append(doc)
                            listings.append(f"{t}: {token_listings}")




        return listings

    @staticmethod
    def factory(docs: Dict):
        index = Search()

        for k,v in docs.items():
            index.add_document(corpus=v, name=k)
        index.index_documents()

        return index
