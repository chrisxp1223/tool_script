from setuptools import setup, find_packages

setup(
    name="dq_map_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
    ],
    entry_points={
        'console_scripts': [
            'generate_header=src.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for generating DQ map header files",
    long_description=open("docs/README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)