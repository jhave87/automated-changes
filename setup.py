import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autochange-joh",
    version="0.1.4",
    author="Jonas Have",
    author_email="joh@sik.dk",
    description="A small package that set up monitoring of directories for xml files. The xml files are used to provide an output to a RPA service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhave87/automated-changes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)