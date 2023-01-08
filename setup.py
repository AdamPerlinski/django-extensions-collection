from setuptools import setup, find_packages

setup(
    name='django-extensions-collection',
    version='0.1.0',
    description='A collection of Django extensions',
    packages=find_packages(),
    install_requires=['Django>=3.2'],
    python_requires='>=3.8',
)
