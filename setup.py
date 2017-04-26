from setuptools import setup


setup(name='shoeboxmail',
    version='0.7',
    description='shoeboxmail',
    classifiers=[
    "Programming Language :: Python",
    ],
    author='',
    author_email='',
    url='',
    keywords='',
    install_requires=[],
    packages=['shoeboxmail'],
    package_dir={'shoeboxmail': 'shoeboxmail'},
    package_data={
        'shoeboxmail': ['templates/*'],
    },
    zip_safe=False,
    entry_points='''
        [console_scripts]
        shoeboxmail=shoeboxmail:cli
    '''
    )
