import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oscar-square",
    version="0.0.1",
    author="Jacob Hume",
    author_email="jacob@fragdev.com",
    description="Square payment integration for Oscar Commerce",
    install_requires=['squareconnect==2.3.*'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://fragdev.com/projects/square-payment-oscar-commerce",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)

