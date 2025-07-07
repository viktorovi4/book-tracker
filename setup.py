from setuptools import setup, find_packages

setup(
    name="book_tracker",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'pytest',
        'allure-pytest'
    ],
)