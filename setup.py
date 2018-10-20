import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # Application name:
    name="breezo",

    # Version number (initial):
    version="1.0.4",

    # Application author details:
    author="nimeshmittal",
    author_email="nimesh.mittal@gmail.com",

    # Packages
    packages=setuptools.find_packages(),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/nimesh-mittal/breezo-sdk",

    # license="LICENSE.txt",
    description="Python package for dynamic centralized configuration manager for microservices",

    install_requires=[
        "requests",
        "pandas"
    ],
)
