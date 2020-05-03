import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="serial-teleinfo",
    version="1.0.1",
    author="Ugo Méda",
    author_email="meda.ugo@gmail.com",
    description="Utilities to connect to a Teleinformation serial device",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ugomeda/serial-teleinfo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    extras_require={"server": ["aiohttp", "http_basic_auth"]},
    install_requires=["pyserial"],
)
