"""The plugin registers its alcf--* shims through the public shim API."""

from __future__ import annotations

import pytest

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_alcf import register_shims

_SHIMS = ("alcf--metis", "alcf--minerva", "alcf--sophia")


@pytest.fixture()
def _registered():
    _reset_registry()  # clean registry, so only the plugin's shims are present
    register_shims()
    yield


@pytest.mark.parametrize("name", _SHIMS)
def test_registers_alcf_shim(_registered, name):
    shim = get_shim(name)
    assert shim is not None
    assert shim.base == "openai_chat"
    assert shim.connection.base_url.startswith(
        "https://inference-api.alcf.anl.gov/resource_server/"
    )
    assert shim.connection.api_key_env == "ALCF_API_KEY"
