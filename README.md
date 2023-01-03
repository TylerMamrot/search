# document search
document search project using an Inverted Index

hacked on after reading a bit of https://nlp.stanford.edu/IR-book/html/htmledition/an-example-information-retrieval-problem-1.html

The purpose of this project is to familiarize myself with basic NLP technques and data strucutes used for text search engines.

In this repo you will find an implementation of an inverted index and a k-gram index

These data structures are used in search.py to create a search engine used to process simple queries.
search.py is exposed through a user friendly cli

To use the search engine you need to do the following.

1.) index the documents you want to search: `search index <doc1, doc2, doc3>
2.) create a query using the cli, here are some examples:
* `search find digital`
* `search find di`

the search engine will search your indexed files and return the list of documents each term belongs in.


### Instructions
`pip install -r requirements.txt`

`pip install -e .`
^ this lets you use the CLI to run the script

`search --help` will give you a list of options to choose from

`search init` to get started

Right now, it will only index plain text files, not compiled files, images or videos docs in the `docs`
