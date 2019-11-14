from setuptools import setup
import os

try:
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    name='env_arg_parser',
    version='6.0.1',
    description="This subclasses python's argparse to automatically accept"
                " environmental variables under the same name.",
    long_description=long_description,
    author='Ben Christenson',
    author_email='Python@BenChristenson.com',
    url='https://github.com/SeabornGames/EnvArgParser',
    install_requires=[
    ],
    extras_require={
    },
    packages=['env_arg_parser'],
    license='MIT License',
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'),
    entry_points='''
        [console_scripts]
        seaborn_table=seaborn_table.table:main
    ''',
)
