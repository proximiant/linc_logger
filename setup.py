import os
import zlib

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 'linclogger/linclogger.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="linclogger",
    version=__version__,
    url="https://git.myserver.com/foobar-utils/",

    author="Astam",
    author_email="astam@letslinc.com",

    description="Linc log formatter.",
    long_description=open('README.rst').read(),
    packages=['linclogger'],
    zip_safe=False,
    platforms='any',

    install_requires=["logmatic-python", "concurrent-log-handler"],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
