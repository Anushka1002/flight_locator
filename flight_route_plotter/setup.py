import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='flight-route-plotter',
    version='0.1',
    packages=["flight_route_plotter"],
    description="library to find sun's position for route of a flight using arrival and departure coordinates along "
                "with arrival and departure datetime.",
    long_description=README,
    author='Anushka',
    author_email='verma.anushka10@gmail.com',
    url='https://sachinmadaan@bitbucket.org/wingman-night-calculator/night_cal_python.git',
    license='',
    install_requires=[
        'asgiref==3.2.7',
        'astral==2.2',
        'geographiclib==1.50',
        'geopy==1.22.0',
        'pytz==2020.1',
        'sqlparse==0.3.1',
    ]
)
