import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    ]

setup(name='shoeboxmail',
    version='0.0',
    description='shoeboxmail',
    classifiers=[
    "Programming Language :: Python",
    ],
    author='',
    author_email='',
    url='',
    keywords='',
    install_requires=requires,
    packages=['shoeboxmail'],
    package_dir={'shoeboxmail': 'shoeboxmail'},
    zip_safe=False,
    entry_points='''
        [console_scripts]
        shoeboxmail=shoeboxmail:cli
    '''
    )
