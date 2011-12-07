from distutils.core import setup

import ciscolib

setup(name="ciscolib",
    packages=['ciscolib'],
    version=ciscolib.__version__,
    description="Interacts with Cisco devices via command line",
    author="Nick Pegg",
    author_email="nick@nickpegg.com",
    url="https://github.com/nickpegg/ciscolib",
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Terminals",
        "Topic :: Terminals :: Telnet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

