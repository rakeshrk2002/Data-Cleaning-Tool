from setuptools import find_packages, setup

def get_requirements(file_path: str):
    """Reads and cleans the requirements.txt file."""
    with open(file_path) as file:
        requirements = file.readlines()
        requirements = [req.strip() for req in requirements if req.strip() and req.strip() != "-e ."]
    return requirements

setup(
    name='Automated_Data_Cleaning_Pipeline',
    version='0.0.1',
    author='Rakesh',
    author_email='rakeshthiagu2002@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
)
