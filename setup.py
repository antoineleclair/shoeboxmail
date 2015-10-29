import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    ]

setup(name='shoeboxsmtp',
    version='0.0',
    description='shoeboxsmtp',
    classifiers=[
    "Programming Language :: Python",
    ],
    author='',
    author_email='',
    url='',
    keywords='',
    install_requires=requires,
    packages=['shoeboxsmtp'],
    package_dir={'shoeboxsmtp': 'shoeboxsmtp'},
    zip_safe=False,
    entry_points='''
        [console_scripts]
        shoeboxsmtp=shoeboxsmtp:cli
    '''
    )
