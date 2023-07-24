import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-picked",
    version="0.5.0",
    author="Ana Paula Gomes",
    author_email="apgomes88@gmail.com",
    maintainer="Ana Paula Gomes",
    maintainer_email="apgomes88@gmail.com",
    license="MIT",
    url="https://github.com/anapaulagomes/pytest-picked",
    description="Run the tests related to the changed files",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.7",
    install_requires=["pytest>=3.7.0"],
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"pytest11": ["picked = pytest_picked.plugin"]},
)
