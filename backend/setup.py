from setuptools import setup, find_packages

setup(
    name="learning-analytics",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-cors",
        "python-dotenv",
    ],
) 