from __future__ import annotations

import hashlib
from pathlib import Path

import click
import yaml
from xarray import DataTree

from swarmpal import get_data, make_process
from swarmpal.express import fac_single_sat as _fac_single_sat
from swarmpal.utils.configs import SPACECRAFT_TO_MAGLR_DATASET
from swarmpal.utils.queries import last_available_time as _last_available_time


@click.group()
def cli():
    pass


@cli.command()
def spacecraft():
    """List names of available spacecraft"""
    spacecraft = list(SPACECRAFT_TO_MAGLR_DATASET.keys())
    click.echo("\n".join(spacecraft))


@cli.command(add_help_option=True)
@click.option(
    "--spacecraft", required=True, help="Check available with: swarmpal spacecraft"
)
@click.option("--time_start", required=True, help="ISO 8601 time")
@click.option("--time_end", required=True, help="ISO 8601 time")
@click.option("--grade", required=True, help="'OPER' or 'FAST'")
@click.option("--to_cdf_file", required=True, help="Output CDF file")
def fac_single_sat(
    spacecraft: str, time_start: str, time_end: str, grade: str, to_cdf_file: str
):
    """Execute FAC single-satellite processor"""
    return _fac_single_sat(spacecraft, time_start, time_end, grade, to_cdf_file)


@cli.command(add_help_option=True)
@click.argument("collection")
def last_available_time(collection):
    """UTC of last available data for a collection, e.g. SW_FAST_MAGA_LR_1B"""
    time = _last_available_time(collection)
    click.echo(time.isoformat())


def _calc_md5sum(filename):
    """Calculate the md5sum of the content of a file"""
    return hashlib.md5(open(filename, "rb").read()).hexdigest()


@cli.command(
    add_help_option=True,
    short_help="Process datasets in batch mode",
    help="Process datasets in batch mode for a given CONFIG file in yaml format",
)
@click.option(
    "--out-dir",
    "out_dir",
    type=Path,
    default=Path("."),
    show_default=True,
    help="Directory prefix for output files.",
)
@click.option(
    "--write-registry",
    "write_registry",
    is_flag=True,
    show_default=True,
    default=False,
    help="Writes a registry.txt file with md5sum",
)
@click.argument("config", type=click.File("r"))
def batch(out_dir: click.Path, write_registry: bool, config: click.File):
    """Run SwarmPAL in batch mode. The datasets and processes need to be specified in YAML file and
    passed as the first CONFIG argument. The results are written to NetCDF files specified by out_dir.

    Parameters
    ----------
    out_dir: Path
        The directory where the results are written to. Defaults to the current directory.
    config: File
        The YAML file that defines the datasets and processes.

        TODO: describe yaml schema

    Examples
    --------
    $ cat config.yaml


    $ swarmpal batch config.yaml

    Will ...
    """
    with open(config.name) as f:
        datasets = yaml.safe_load(f)

    registry = {}
    for name, dataset in datasets.items():
        data = DataTree()
        for dataset_config in dataset["data"]:
            item = get_data(**dataset_config)
            for key, dt in item.children.items():
                data[key] = dt

        # Apply processes
        for process_spec in dataset.get("processes", []):
            process = make_process(**process_spec)
            data = process(data)

        # Save the results as a NetCDF file
        filename = f"{name}.nc4"
        filepath = out_dir / filename

        data.to_netcdf(filepath)
        if write_registry:
            registry[filename] = _calc_md5sum(filepath)

    if write_registry:
        registry_name = out_dir / "registry.txt"
        with open(registry_name, "w") as f:
            for filename, md5sum in registry.items():
                f.write(f"{filename} md5:{md5sum}\n")
