import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="callirhoe", 
    version="0.4.4",
    author="geotz",
    author_email="",
    description="pdf calendar creator with high quality vector graphics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geotz/callirhoe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
