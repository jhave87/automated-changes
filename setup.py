import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autochange-joh", # Replace with your own username
    version="0.0.1",
    author="Jonas Have",
    author_email="joh@sik.dk",
    description="A small package that monitors a directory for xml files and provides output to an RPA process.",
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