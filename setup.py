from setuptools import setup, find_packages


setup(
    name='odc',
    author='Pedro Rodriguez',
    author_email='ski.rodriguez@gmail.com',
    maintainer='Pedro Rodriguez',
    maintainer_email='ski.rodriguez@gmail.com',
    license='Apache License V2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'test']),
    version='0.0.0',
    install_requires=['click', 'pandas', 'smart_open'],
    entry_points={
        'console_scripts': ['odc = odc:cli']
    }
)
