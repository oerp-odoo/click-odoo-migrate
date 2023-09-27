#!/usr/bin/env python
from __future__ import annotations

import importlib
from pathlib import Path

import click
import click_odoo

from .utils import SORT_ALG_MAPS, do_sorted, parse_path

MIG_EXT = ".py"
DEFAULT_SORT_ALG = "sorted"


@click.command()
@click_odoo.env_options(default_log_level="warn", with_rollback=True)
@click.argument(
    "path",
    nargs=1,
    required=1,
)
@click.option(
    "--force",
    "-f",
    multiple=True,
    help=(
        "Specify migration file names (without extension) to force migrate. "
        "It will migrate even if it was already migrated. Must be subset of "
        "migration files provided in a path."
    ),
)
@click.option(
    "--sort-algorithm",
    "-s",
    help=(
        "Sort algorithm to sort migration files before migration. "
        f"Possible choices: {', '.join(SORT_ALG_MAPS.keys())}"
    ),
    default=DEFAULT_SORT_ALG,
)
def main(env, path: str, force: list, sort_algorithm=DEFAULT_SORT_ALG):
    """Run migration scripts using odoo env.

    PATH:  migration file or directory of migration files.

    Migration file must end with .py extension and must have 'migrate' function
    that expects 'env' and 'shared_data' argument.

    'shared_data' argument is a dictionary that collects previous
    migration scripts returned values (key is migration script name).
    If return (of 'migrate' function) is None, it is not included in
    shared_data.
    """
    if force:
        msg = ", ".join(force)
        click.echo(click.style(f"Force Migrating: {msg}", fg="yellow"))
    migrate(env, path, force=force, sort_algorithm=sort_algorithm)


def migrate(
    env, path: str, force: None | list = None, sort_algorithm=DEFAULT_SORT_ALG
) -> list[Path]:
    if force is None:
        force = []
    cr = env.cr
    mig_paths = do_sorted(parse_path(path, ext=MIG_EXT), sort_algorithm)
    init_migration_table(cr)
    migrated = []
    shared_data = {}
    for mig_path in mig_paths:
        mig_name = mig_path.stem
        if mig_name in force:
            delete_migration_entry(cr, mig_name)
        if is_migrated(cr, mig_name):
            continue
        print(f"Migrating: {mig_name}")
        res = _migrate(env, mig_path, shared_data)
        # Share previous migration script data with others in line.
        if res is not None:
            shared_data[mig_name] = res
        migrated.append(mig_path)
    return migrated


def init_migration_table(cr):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS xodoo_migration (
            name varchar(160) NOT NULL,
            create_date timestamp NOT NULL DEFAULT NOW(),
            CONSTRAINT xodoo_migration_uniq_name UNIQUE (name),
            PRIMARY KEY (name)
        )
        """
    )


def delete_migration_entry(cr, mig_name):
    cr.execute("DELETE FROM xodoo_migration WHERE name = %s", (mig_name,))


def _migrate(env, path: Path, shared_data: dict):
    module = load_script(path)
    try:
        res = module.migrate(env, shared_data)
    except Exception as e:
        raise click.ClickException(
            f"Something went wrong migrating '{path}': {e}"
        ) from e
    save_migration_ref(env.cr, path.stem)
    return res


def is_migrated(cr, name):
    cr.execute("SELECT count(*) FROM xodoo_migration WHERE name = %s", (name,))
    return bool(cr.fetchone()[0])


def save_migration_ref(cr, name):
    cr.execute("""INSERT INTO xodoo_migration VALUES (%s)""", (name,))


def load_script(path: Path):
    module_name = path.stem.lower()
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
