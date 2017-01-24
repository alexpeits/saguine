from setuptools import setup, find_packages

setup(
    name='saguine',
    version=0.1,
    author='Alex Peitsinis',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'saguine = saguine.engine:main'
        ]
    },
    install_requires=[
        'Jinja2==2.8',
        'Markdown==2.6.6',
        'Pygments==2.1.3',
        'PyYAML==3.12'
    ],
    include_package_data=True,
    zip_safe=False
)
