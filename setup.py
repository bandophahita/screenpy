from os import path

from setuptools import setup


requires = [
    "PyHamcrest>=1.9.0,<2",
    "pytest>=4.3.0,<4.4",
    "allure-pytest>=2.6.0,<2.7",
    "selenium>=3.141.0,<3.2"
]

repo_dir = path.abspath(path.dirname(__file__))
about = {}
with open(path.join(repo_dir, 'requests', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    packages=["screenpy"],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: BDD",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
    ],
)