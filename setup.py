from setuptools import setup, find_packages

setup(
    name="hiollama",
    version="0.5",
    description="A friendly CLI for interacting with Ollama language models.",
    author="Ollie McDaniel",
    packages=find_packages(),  # Automatically find all packages in the project
    install_requires=[
        "ollama",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "hiollama=hiollama.__main__:main",
        ],
    },
)