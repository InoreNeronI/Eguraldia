from pathlib import Path
# @see https://stackoverflow.com/a/57191701/16711967
try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements
from setuptools import setup

with Path('requirements/prod.txt').open() as requirements_txt:
    requirements = [
        str(requirement)
        for requirement
        in parse_requirements(filename=requirements_txt, session=PipSession())

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
    install_requires=requirements,
    python_requires='>=3.8',
)
