# Copyright 2023 Timefordev (<https://timefordev.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="xodoo",
    description="Odoo CLI Tools",
    long_description="\n".join((open(os.path.join(here, "README.rst")).read(),)),
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
    setup_requires=["setuptools-scm"],
    install_requires=["click-odoo>=1.3.0", "natsort>=8.4.0"],
    python_requires=">=3.9",
    license="LGPLv3+",
    author="Andrius Laukavičius",
    author_email="info@timefordev.com",
    url="http://github.com/oerp-odoo/xodoo",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        + "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Odoo",
    ],
    entry_points="""
        [console_scripts]
        xodoo-migrate=xodoo.migration:main
    """,
)
