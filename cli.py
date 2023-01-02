import os
import pathlib
import pickle

import click
from search import Search

SEARCH_DIR = ".search"

SEARCH_HOME_PATH = pathlib.Path(pathlib.Path.home(), SEARCH_DIR)


@click.group()
def cli():
    pass


@click.command()
def init():
    """
    Initalize cli
    """
    root = input("File or directory path to start indexing: ")
    click.echo(f"Indexing your documents at {root}")
    files = []
    files = get_file_paths(root, files)
    engine = create_searcher(files)
    click.echo("saving engine...")
    to_file(engine)
    click.echo("engine saved!")


@click.command()
@click.argument("query")
def find(query):
    engine = from_file()
    results = engine.search(query)
    _ = [click.echo(r) for r in results]


@click.command()
def update():
    """
    Index ad hoc docs
    """
    pass


@click.command()
def tune():
    """
    TODO: adhoc parameter chagnes to search engine
    """
    pass


def get_file_paths(root, files):
    for dirpath, subdirs, child_files in os.walk(root):
        for f in child_files:
            if f.endswith(".txt"):
                print(f)
                files.append(os.path.join(dirpath, f))
        for s in subdirs:
            print(s)
            get_file_paths(s, files)

    return files

def to_file(engine):
    """
    serialize search engine object to a file
    """
    create_search_directory()
    with open(pathlib.Path(SEARCH_HOME_PATH,'search.pickle'), 'wb') as file:
        pickle.dump(engine, file)

def from_file():
    """
    load the engine from a file
    """
    with open(pathlib.Path(SEARCH_HOME_PATH,'search.pickle'), 'rb') as file:
       return pickle.load(file)

def create_search_directory():
    if not pathlib.Path.exists(SEARCH_HOME_PATH):
        pathlib.Path.mkdir(SEARCH_HOME_PATH)

def create_searcher(file_paths):
    docs = {f: open(f, 'r').read() for f in file_paths}
    return Search.factory(docs)

cli.add_command(init)
cli.add_command(find)



if __name__ == "__main__":
    cli()