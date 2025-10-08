from setuptools import setup, find_packages

setup(
    name="credit-scan-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)