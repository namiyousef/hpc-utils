from setuptools import setup, find_packages
import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='hpcutils',
    version=get_version("hpcutils/__init__.py"), #'0.0.12',
    description='A package for running job scripts with ease',
    author='Yousef Nami',
    author_email='namiyousef@hotmail.com',
    url='https://github.com/namiyousef/hpc-utils',
    install_requires=[
        'flask',
        'connexion[swagger-ui]'
    ],
    #package_data={}
    packages=find_packages(exclude=('tests*', 'experiments*')),
    package_data={'': ['api/specs/api.yaml', 'helpers/*.sh', 'scripts/*sh', 'templates/*sh']},
    include_package_data=True,
    license='MIT',
    entry_points={
        'console_scripts': ['hpcutils-api=hpcutils.run_api:main', 'hpcutils-worker=hpcutils.run_worker'],
    }
)