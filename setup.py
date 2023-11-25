from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

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
    install_requires=required,
    python_requires='>=3.6',
)
