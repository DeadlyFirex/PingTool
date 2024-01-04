from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PingTool',
    version='v1.2.1',
    url='https://github.com/DeadlyFirex/PingTool',
    license='MIT',
    license_file='LICENSE',
    author='deadly',
    author_email='',
    description='Small application written in Python, socket-based. to ping annoying colleague\'s who won\'t respond.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/DeadlyFirex/PingTool/issues",
    },
    packages=find_packages(),
    platforms="any",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "loguru>=0.7.0",
        "setuptools>=69.0.3"
    ],
    python_requires=">=3.10",
    setup_requires=["setuptools>=69.0.0"],
)
