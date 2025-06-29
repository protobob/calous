from setuptools import setup, find_packages
from calous.constants import APP_VERSION

setup(
    name="calous",
    version=APP_VERSION,  # Use the centralized version constant
    description="Context Abstraction Layer Over Unix Sockets - A friendly CLI for interacting with Ollama language models.",
    author="Ollie McDaniel",
    packages=find_packages(),  # Automatically find all packages in the project
    install_requires=[
        "ollama",
        "requests",
        "rich",
        "asteval",  # For calculator plugin safe mathematical evaluation
    ],
    entry_points={
        "console_scripts": [
            "calous=calous.__main__:main",
        ],
    },
)