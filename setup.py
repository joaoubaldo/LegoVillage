import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'arduino-python',
    ]

setup(name='legovillage',
      version="0.9",
      description='legovillage',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet"
        ],
      author='Joao Coutinho',
      author_email='me at joaoubaldo.com',
      url='http://b.joaoubaldo.com',
      keywords='arduino led leds lego',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="legovillage",
      entry_points={
        'console_scripts':
            ['legovillage = legovillage:main']
        }
      )
