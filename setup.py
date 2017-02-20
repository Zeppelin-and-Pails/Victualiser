"""
setup.py for z&p victualiser.

"""
from distutils.core import setup

setup(
    name = "victualiser",
    packages = ["victualiser", "twitter", "ui"],
    version = "0.1.1",
    description = "Configuarble data pipeline",
    author = "KMR",
    author_email = "github@kerrymr.com",
    url = "http://http://zeppelin-and-pails.com//",
    download_url = "https://github.com/Zeppelin-and-Pails/Victualiser/archive/master.zip",
    keywords = ["data", "feed"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        ],
    install_requires=[
        "luigi",
        "pandas",
        "numpy",
        "textblob",
    ],
    long_description = """\
Victualiser - data feeds
----------------------------------------
A configiurable pipeline pulling from all your favourite platforms.

This version requires Python 3 or later;
""",
)
