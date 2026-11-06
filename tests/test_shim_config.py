"""Parity of the packaged shims with the built-ins they replace."""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry
from llm_rosetta.transforms import apply_transforms

from llm_rosetta_shim_alcf import register_shims

SHIMS = (
    "alcf_metis--chat_completions",
    "alcf_minerva--chat_completions",
    "alcf_sophia--chat_completions",
)


@pytest.fixture(autouse=True)
def _registered():
    _reset_registry()
    register_shims()
    yield
    _reset_registry()


@pytest.mark.parametrize("name", SHIMS)
def test_shim_uses_the_canonical_format_pair(name):
    shim = get_shim(name)
    assert shim is not None
    assert shim.model_type == "llm"
    assert shim.format == "chat_completions"


def test_sophia_clamps_the_effort_ladder():
    """vLLM answers 500 outside low/medium/high, so the range must reach it."""
    shim = get_shim("alcf_sophia--chat_completions")
    assert shim is not None
    assert shim.reasoning is not None
    assert shim.reasoning.effort_field == "reasoning_effort"
    assert shim.reasoning.effort_range == ("low", "high")


def test_sophia_renames_reasoning_on_message_and_delta():
    """vLLM exposes ``reasoning``; the converter reads ``reasoning_content``."""
    shim = get_shim("alcf_sophia--chat_completions")
    assert shim is not None
    body = {
        "choices": [
            {
                "message": {"reasoning": "non-streaming"},
                "delta": {"reasoning": "streaming"},
            }
        ]
    }
    out = apply_transforms(shim.pre_ir_transforms, body)
    choice = out["choices"][0]
    assert choice["message"]["reasoning_content"] == "non-streaming"
    assert choice["delta"]["reasoning_content"] == "streaming"
    assert "reasoning" not in choice["message"]
    assert "reasoning" not in choice["delta"]


@pytest.mark.parametrize("name", SHIMS)
def test_model_list_transform_is_exported(name):
    from llm_rosetta_shim_alcf.providers.alcf import model_utils

    assert callable(model_utils.make_alcf_model_list_transform)


def test_the_three_clusters_share_a_group():
    for name in SHIMS:
        shim = get_shim(name)
        assert shim is not None
        assert shim.group == "alcf"


@pytest.mark.parametrize("name", SHIMS)
def test_the_credential_comes_from_the_vendor_manifest(name):
    """The manifest holds the credential once; each leaf only adds its URL."""
    shim = get_shim(name)
    assert shim is not None
    assert shim.manifest is not None
    assert shim.manifest.path.name == "provider.yaml"
    assert shim.connection.api_key_env == "ALCF_API_KEY"
    assert shim.connection.token_command is not None
    exchange = shim.connection.token_command[-1]
    assert exchange.endswith("providers/alcf/mint_token.py")
    assert Path(exchange).is_file()
