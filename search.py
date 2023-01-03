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
        # main dict used to track term and what doc they are listed in
        self.index: Dict[str:set] = {}
        # k gram index to suport fuzzy searching
        self.k_gram_index: Dict[str:set] = {}
        # contains listing index and stemmed representation of tokens
        self.docs: Dict[int: str] = {}
        # dict of document index and corresponding document names
        self.doc_names: Dict[int: str] = {}
        self.doc_number = 0  # tracks number of docs indexed, used to add keys to self.docs
        self.tokenizer = RegexpTokenizer(r'\w+')  # tokenize words only
        self.stemmer = PorterStemmer()  # standard stemmer

    def print(self):
        _ = [print(f"{k}: {len(v)}: {v}") for k, v in self.index.items()]

    def _get_kgrams(self):
        _ = [print(f"{k}: {len(v)}: {v}")
             for k, v in self.k_gram_index.items()]

    def add_document(self, corpus: str, name: str):
        """
        assign index to a document and apply preprocessing, does not reindex engine

        In reality, document would probably be written to disk somewhere
        """
        self.doc_number += 1
        tokens = self.tokenizer.tokenize(corpus)

        filtered_words = [
            t for t in tokens if t not in stopwords.words('english')]
        stemmed_words = [self.stemmer.stem(w) for w in filtered_words]

        # track stemmed words in dict with doc
        self.docs[self.doc_number] = stemmed_words
        self.doc_names[self.doc_number] = name  # match doc number to doc name

    def index_documents(self):
        """
        Indexes each document into inverted index and k gram inverted index
        :return:
        """
        #  empty current index and start from scratch
        self.index = {}
        self.k_gram_index = {}

        for k, document in self.docs.items():
            # index stemmed tokens
            for token in document:
                if not self.index.get(token):
                    self.index[token] = set()

                # index bi-grams
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

        results = []

        match = self.get(stemmed_token)
        if match:
            results = [self.doc_names[l] for l in match]
        else:
            # fall back to k gram search if we get no result for the original query
            grams = bigrams(stemmed_token)
            for gram in grams:
                # get all tokens associated with bi-gram
                tokens = self.get_kgram(gram)
                if tokens:
                    for t in tokens:
                        # stem again here because the kgram index isnt' stemmed
                        listing = self.get(t)
                        token_listings = []
                        if listing:
                            for l in listing:
                                doc = self.doc_names[l]
                                token_listings.append(doc)
                             # for kgrams search, append the token associated wit the kgrams and a list of documents associated with that word
                            results.append(f"{t}: {token_listings}")
        return results

    @staticmethod
    def factory(docs: Dict):
        """
        Index a dictionary of text
        """
        index = Search()

        for k, v in docs.items():
            index.add_document(name=k, corpus=v,)

        index.index_documents()

        return index
