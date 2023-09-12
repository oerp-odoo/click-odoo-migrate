import glob
from pathlib import Path

import click
from natsort import natsorted

SORT_ALG_MAPS = {"sorted": sorted, "natsorted": natsorted}


def parse_path(path: str, ext=".py") -> list[Path]:
    p = Path(path)
    if not p.exists():
        raise click.ClickException(f"Path ({path}) does not exist")
    if p.is_dir():
        return [Path(file) for file in glob.glob(f"{path}/*{ext}")]
    elif p.suffix == ext:
        return [p]
    raise click.ClickException(f"File must end with {ext} extension.")


def do_sorted(items, algname: str, **kw):
    try:
        alg = SORT_ALG_MAPS[algname]
        return alg(items, **kw)
    except KeyError:
        raise ValueError(f"Unsupported sorting algorithm used: {algname}")
