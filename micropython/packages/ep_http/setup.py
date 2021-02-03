import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")
import sdist_upip

with open("README.md", "r", encoding="utf-8") as fh:
     long_description = fh.read()

setup(
    name="micropython_eydam-prototyping_ep_http",
    version="0.0.2",
    author="Tobias Eydam",
    author_email="eydam-prototyping@outlook.com",
    description="Some wifi functions for MicroPython",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/packages/ep_http",
    classifiers=[
        "Programming Language :: Python :: Implementation :: MicroPython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={'sdist': sdist_upip.sdist},
    install_requires=['ep_config'],
    py_modules=['ep_http']
)