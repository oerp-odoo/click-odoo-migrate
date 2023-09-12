#!/usr/bin/env python
import os
import subprocess
import sys

odoo_branch = sys.argv[1]
odoo_dir = sys.argv[2]


def odoo_installed():
    try:
        import odoo  # noqa
    except ImportError:
        return False
    else:
        return True


def odoo_cloned():
    return os.path.isdir(os.path.join(odoo_dir, ".git"))


def clone_odoo():
    subprocess.check_call(
        [
            "git",
            "clone",
            "--depth=1",
            "-b",
            odoo_branch,
            "https://github.com/odoo/odoo",
            odoo_dir,
        ]
    )


def install_odoo():
    subprocess.check_call(
        [
            "pip",
            "install",
            "--no-binary",
            "psycopg2",
            "-r",
            "https://raw.githubusercontent.com/OCA/OCB/{}/requirements.txt".format(
                odoo_branch
            ),
        ]
    )
    subprocess.check_call(["pip", "install", "-e", odoo_dir])


def main():
    if not odoo_installed():
        if not odoo_cloned():
            clone_odoo()
        install_odoo()


if __name__ == "__main__":
    main()
