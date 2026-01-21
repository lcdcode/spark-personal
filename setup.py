from setuptools import setup, find_packages

setup(
    name="spark-personal",
    version="1.0.0",
    description="Personal knowledgebase and snippet manager for programmers",
    author="SPARK",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "PyYAML>=6.0",
        "Pygments>=2.17.0",
        "Markdown>=3.5.0",
    ],
    entry_points={
        "console_scripts": [
            "spark=spark.main:main",
        ],
    },
    python_requires=">=3.8",
)
