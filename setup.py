from setuptools import setup, find_packages

setup(
    name="gitiles",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gitiles=gitiles.cli:main',
        ],
    },
    author="Shivam Jain",
    author_email="shivamjain.dev@gmail.com",
    description="A CLI tool to manage multiple Git profiles",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)