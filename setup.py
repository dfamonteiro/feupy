# https://packaging.python.org/tutorials/packaging-projects/
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="feupy",
    version="0.4.4",
    author="Daniel Monteiro",
    author_email="up201806185@fe.up.pt",
    description="The sigarra scraping library no one asked for",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/up201806185/feupy",

    python_requires='>=3.6',
    install_requires=required,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)