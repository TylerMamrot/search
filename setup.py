from setuptools import setup

setup(
    name='search',
    version='0.1.0',
    py_modules=['cli'],
    install_requires=[
        'Click',
        'nltk',
        'typing',
    ],
    entry_points={
        'console_scripts': [
            'search = cli:cli',
        ],
    },
)