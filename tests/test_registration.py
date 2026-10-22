"""The plugin registers its alcf_<cluster>--chat_completions shims via the public shim API."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_alcf import register_shims

_CLUSTERS = ("metis", "minerva", "sophia")
_SHIMS = tuple(f"alcf_{cluster}--chat_completions" for cluster in _CLUSTERS)

# The three clusters share one admin top level; `display_name` is this shim's own
# row label inside it (rendered as "<display_name> · chat_completions").
_GROUP = "alcf"
_DISPLAY_NAMES = {"metis", "minerva", "sophia"}

_PROVIDERS_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "llm_rosetta_shim_alcf"
    / "providers"
    / "alcf"
)


def _provider_config(cluster: str) -> dict:
    """The raw ``provider.yaml`` of one cluster, parsed as data."""
    path = _PROVIDERS_DIR / cluster / "provider.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture()
def _registered():
    _reset_registry()  # clean registry, so only the plugin's shims are present
    register_shims()
    yield


@pytest.mark.parametrize("name", _SHIMS)
def test_registers_alcf_shim(_registered, name):
    shim = get_shim(name)
    assert shim is not None
    assert shim.base == "chat_completions"
    assert shim.connection.base_url.startswith(
        "https://inference-api.alcf.anl.gov/resource_server/"
    )
    assert shim.connection.api_key_env == "ALCF_API_KEY"


@pytest.mark.parametrize("cluster", _CLUSTERS)
def test_provider_yaml_declares_canonical_name_and_grouping(cluster):
    """``group`` is read from the YAML on purpose: the parent surfaces it on
    ``ProviderShim`` only in current releases, so the contract is pinned where
    the plugin actually declares it."""
    cfg = _provider_config(cluster)
    assert cfg["name"] == f"alcf_{cluster}--chat_completions"
    assert cfg["model_type"] == "llm"
    assert cfg["format"] == "chat_completions"
    assert cfg["group"] == _GROUP
    assert cfg["display_name"] == cluster


def test_alcf_shims_declare_one_group_and_distinct_labels(_registered):
    assert {_provider_config(c)["group"] for c in _CLUSTERS} == {_GROUP}
    assert {get_shim(name).display_name for name in _SHIMS} == _DISPLAY_NAMES


@pytest.mark.parametrize("name", _SHIMS)
def test_the_credential_exchange_ships_with_the_shim(_registered, name):
    """A provider needs no ``token_command``: the shim declares one.

    The relative argument is resolved against the provider's own directory by
    the loader, so this loads the shims for real and checks the script exists —
    the failure mode is a path that only exists in a source checkout.
    """
    shim = get_shim(name)
    assert shim is not None
    argv = shim.connection.token_command
    assert argv is not None and argv[0] == "python3"
    script = Path(argv[1])
    assert script.is_absolute() and script.is_file(), argv
    assert script.name == "token.py"
