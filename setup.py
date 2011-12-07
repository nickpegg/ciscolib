from distutils.core import setup

import ciscolib

setup(name="ciscolib",
    version=ciscolib.__version__,
    description="Interacts with Cisco devices via command line",
    author="Nick Pegg",
    author_email="nick@nickpegg.com",
    packages=['ciscolib'],
    )

