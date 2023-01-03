import sys

import os
import pathlib
import pickle

import click
from search import Search

from typing import Dict, List, Set

SEARCH_DIR = ".search"

SEARCH_HOME_PATH = pathlib.Path(pathlib.Path.home(), SEARCH_DIR)


@click.group()
def cli():
    pass


@click.command()
def init():
    """
    Initalize cli, create search engine object and save it to a file.
    """
    root = input("File or directory path to start indexing: ")
    click.echo(f"Indexing your documents at {root}")

    files = get_file_paths(root)
    engine = create_engine(files)

    click.echo("saving engine...")
    to_file(engine)

    click.echo("engine saved!")


@click.command()
@click.argument("query")
def find(query):
    """
    find word in indexed docs, or similar words if query cannot be satisfied
    """
    engine = from_file()
    results = engine.search(query)
    _ = [click.echo(r) for r in results]


@click.command()
@click.argument("path")
def update(path):
    """
    Index ad hoc documents
    PATH: path to begin indexing, can be a file or directory
    """
    click.echo(f"Indexing at {path}")
    engine = from_file()

    files: List[pathlib.Path] = get_file_paths(path)

    for f in files:
        corpus = read_file(f)
        if corpus:
            engine.add_document(corpus, str(f))
        else:
            click.echo(f"WARNING {f} is empty not indexing")

    engine.index_documents()
    to_file(engine)


@click.command()
def tune():
    """
    TODO: adhoc parameter chagnes to search engine
    """
    pass


@click.command()
@click.option("--files", default=False, type=bool)
@click.option("--tokens", default=False, type=bool)
@click.option("--kgrams", default=False, type=bool)
def info(files, tokens, kgrams):
    """
    Info about the search engine
    """
    engine = from_file()
    if files:
        name = engine.get_document_names()
        for k, v in name.items():
            click.echo(f"{k}:{v}")

    if tokens:
        click.echo(engine.print())

    if kgrams:
        click.echo(engine._get_kgrams())


def get_file_paths(path):
    """
    Get files at the path, will walk direcory structure or read a plain ole file.
    """
    files = []

    path = pathlib.Path(path)

    if not pathlib.Path.exists(path):
        click.echo(f"WARNING: {path} does not exist")
        return sys.exit(1)

    if pathlib.Path(path).is_dir():
        click.echo(f"Walking dir {path}")
        for dirpath, subdirs, child_files in os.walk(path):
            for f in child_files:
                files.append(str(pathlib.Path(dirpath, f)))
            for s in subdirs:
                files += get_file_paths(pathlib.Path(dirpath, s))

    if pathlib.Path(path).is_file():
        files.append(path)

    return files


def to_file(engine):
    """
    serialize search engine object to a file
    """
    create_search_directory()
    with open(pathlib.Path(SEARCH_HOME_PATH, 'search.pickle'), 'wb') as file:
        pickle.dump(engine, file)


def from_file():
    """
    load the engine from a file
    """
    with open(pathlib.Path(SEARCH_HOME_PATH, 'search.pickle'), 'rb') as file:
        return pickle.load(file)


def create_search_directory():
    """
    create directory to store serialized search engine file
    """
    if not pathlib.Path.exists(SEARCH_HOME_PATH):
        pathlib.Path.mkdir(SEARCH_HOME_PATH)


def create_engine(files):
    """
    create Search object using file paths.
    """
    docs: Dict = collect_files(files)
    if not docs:
        click.echo(
            "WARNING: No documents were read, nothing for engine to index.")
        sys.exit(1)
    else:
        return Search.factory(docs)


def collect_files(files):
    """
    collect files into dict.
    preprocessing step to feed into Search class
    """
    docs = {}
    for file in files:
        corpus = read_file(file)
        if corpus:
            docs[file] = corpus
        else:
            click.echo(f"WARNING {file} is empty not indexing")
    return docs


def read_file(file):
    """
    read file into string
    """
    path = pathlib.Path(file)
    try:
        f = open(path, 'r').read()
        return f
    except UnicodeDecodeError:
        click.echo(f"WARNING: will not index binary file: {path}")


# register commands with cli
cli.add_command(init)
cli.add_command(find)
cli.add_command(update)
cli.add_command(info)


if __name__ == "__main__":
    cli()
