from setuptools import setup, find_packages

with open('README.rst') as tmp_file:
    readme = tmp_file.read()

with open('LICENSE') as tmp_file:
    license = tmp_file.read()

setup(
    name='Modify',
    version='0.1.0dev',
    description='For modifying Sptify playlists based on most listened songs',
    long_description=readme,
    author='Trevor Medina',
    url='https://github.com/mongoishere/modify',
    license=license,
    packages=find_packages(exclude=(
        'docs',
        'tests',
        '.vscode'
    ))
)