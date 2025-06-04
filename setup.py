from setuptools import setup, find_packages
from hiollama.constants import APP_VERSION

setup(
    name="hiollama",
    version=APP_VERSION,  # Use the centralized version constant
    description="A friendly CLI for interacting with Ollama language models.",
    author="Ollie McDaniel",
    packages=find_packages(),  # Automatically find all packages in the project      install_requires=[
        "ollama",
        "requests",
        "rich",
        "asteval",  # For calculator plugin safe mathematical evaluation
    ],
    entry_points={
        "console_scripts": [
            "hiollama=hiollama.__main__:main",
        ],
    },
)