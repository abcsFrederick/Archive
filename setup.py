from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import call

with open('README.rst') as readme_file:
    readme = readme_file.read()

class CustomInstall(install):
    def run(self):
        install.run(self)
        call(['pip', 'install', 'pycurl', '--global-option=--with-openssl'])

requirements = [
    'girder>=3',
    'psycopg2-binary',
    'mysql-connector',
    'requests==2.31.0'
]

setup(
    author='Tianyi Miao',
    author_email='tymiao1220@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='Girder v3 adaptation of Archive',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='girder-plugin, archive_girder3',
    name='girder-archive',
    packages=find_packages(exclude=['plugin_tests']),
    url='https://github.com/abcsFrederick/archive',
    version='0.1.0',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'archive = girder_archive:ArchivePlugin'
        ]
    },
    cmdclass={
        'installPycurl': CustomInstall
    }
)