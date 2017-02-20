"""
setup.py for z&p victualiser.

"""
from setuptools import setup, find_packages
import os, io

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, 'README.md'), 'r') as f:
    __long_description__ = f.read()

__project__      = "victualiser"
__version__      = "0.1.1"
__license__      = 'MIT License'
__keywords__     = "modular data pipeline"
__url__          = "http://zeppelin-and-pails.com/"
__download_url__ = "https://github.com/Zeppelin-and-Pails/Victualiser/archive/master.zip"
__platform__     = "Console"

__author__       = "KMR"
__author_email__ = "github@kerrymr.com"

__classifiers__ = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Linguistic",
    "Environment :: Console",
]

__install_requires__ = [
    "luigi",
    "pandas",
    "numpy",
    "textblob",
    "matplotlib",
]

__extra_requires__ = {
    'test':  ['pytest', 'coverage', 'mock'],
}

def main():
    setup(
        name                 = __project__,
        version              = __version__,
        license              = __license__,
        url                  = __url__,
        download_url         = __download_url__,
        keywords             = __keywords__,
        description          = "{} - {}".format(__project__, __keywords__),
        long_description     = __long_description__,
        author               = __author__,
        author_email         = __author_email__,
        packages             = find_packages(),
        include_package_data = True,
        classifiers          = __classifiers__,
        install_requires     = __install_requires__,
        extras_require       = __extra_requires__,
    )

if __name__ == '__main__':
    main()
