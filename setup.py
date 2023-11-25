# @see https://stackoverflow.com/a/16624700/16711967
from pathlib import Path
from pkg_resources import parse_requirements
from setuptools import setup

with Path('requirements/prod.txt').open() as requirements_txt:
    reqs = [
        str(requirement)
        for requirement
        in parse_requirements(requirements_txt)]

setup(
    name='WebUI',
    version='1.0.0',
    author='Nick Johnstone, Martin Mozos',
    author_email='ncwjohnstone@gmail.com, martinmozos@gmail.com',
    packages=['webui'],
    scripts=['src/main.py'],
    url='https://github.com/InoreNeronI/Eguraldia',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    description='WebUI lets you create first class desktop applications in Python with HTML/CSS',
    long_description=open('README.md').read(),
    install_requires=reqs,
    python_requires='>=3.6',
)
