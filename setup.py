import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stravatools-pkg-arnaud.duval", # Replace with your own username
    version="0.0.1",
    author="Arnaud Duval",
    author_email="arnaud.duval@gmail.com",
    description="Tools to handle Strava data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://aduval.fr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
