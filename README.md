# How to create build and upload to PyPI

python3 setup.py sdist bdist_wheel
twine upload dist/*

# How to use the package

pip install breezo

from breezo.client import ConfigClient
c = ConfigClient()
print(c.display())
