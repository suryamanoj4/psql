from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("pyproject.toml", "r", encoding="utf-8") as fh:
    lines = fh.readlines()
    for line in lines:
        if line.startswith("version = "):
            version = line.split("=")[1].strip().strip('"')
            break

setup(
    name="pyql",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="The Universal, Lazy, Super-Friendly Querying Toolkit for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[],
)