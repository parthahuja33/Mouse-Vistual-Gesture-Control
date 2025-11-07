"""Setuptools configuration for the Virtual Mouse project."""

from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


def read_requirements() -> list[str]:
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        return []
    return [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines() if line.strip()]


setup(
    name="virtual-mouse",
    version="2.0.0",
    description="Camera powered virtual mouse controlled by hand gestures.",
    author="Virtual Mouse Contributors",
    package_dir={"": "."},
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=read_requirements(),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["virtual-mouse=src.main:main"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Topic :: Multimedia :: Video",
    ],
    license="MIT",
)

