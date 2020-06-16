import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='flight-path-locator',
    version='0.1',
    packages=["flight_locator"],
    description="library to find sun's position for route of a flight using arrival and departure coordinates.",
    long_description=README,
    author='Anushka',
    author_email='verma.anushka10@gmail.com',
    url='https://github.com/Anushka1002/Projects',
    license='MIT',
    install_requires=[
        'asgiref==3.2.7',
        'astral==2.2',
        'geographiclib==1.50',
        'geopy==1.22.0',
        'pytz==2020.1',
        'sqlparse==0.3.1',
    ]
)
