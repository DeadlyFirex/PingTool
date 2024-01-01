from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as req:
    requirements = [i.strip() for i in req.readlines()]

setup(
    name='PingTool',
    version='1.0.0',
    url='https://github.com/DeadlyFirex/PingTool',
    license='MIT',
    author='deadly',
    author_email='',
    description='Small application written in Python, socket-based. to ping annoying colleague\'s who won\'t respond.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/DeadlyFirex/PingTool/issues",
    },

    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU AGPLv3 License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.10",
)
