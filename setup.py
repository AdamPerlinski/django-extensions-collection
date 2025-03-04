from setuptools import setup, find_packages

setup(
    name='django-extensions-plus',
    version='1.0.0',
    description='A collection of 30+ custom Django extensions',
    author='Django Extensions',
    author_email='extensions@example.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'Django>=3.2',
        'cryptography>=3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-django>=4.5',
            'pytest-cov>=4.0',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
