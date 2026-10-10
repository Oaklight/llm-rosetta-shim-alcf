# llm-rosetta-shim-alcf

ALCF (Argonne Leadership Computing Facility) provider shims for
[llm-rosetta](https://github.com/Oaklight/llm-rosetta), delivered as a **plugin
package** rather than as built-in shims.

Standalone-repository variant of
[llm-rosetta#666](https://github.com/Oaklight/llm-rosetta/issues/666), verifying the
plugin shim loader ([#272](https://github.com/Oaklight/llm-rosetta/issues/272) /
[#273](https://github.com/Oaklight/llm-rosetta/issues/273)) against a real shim set.
The built-in `alcf--*` shims stay in llm-rosetta for now.

## Shims

| Shim | Base | Endpoint |
|:---|:---|:---|
| `alcf--metis` | `openai_chat` | `https://inference-api.alcf.anl.gov/resource_server/metis/api/v1` |
| `alcf--minerva` | `openai_chat` | `https://inference-api.alcf.anl.gov/resource_server/minerva/api/v1` |
| `alcf--sophia` | `openai_chat` | `https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1` |

Model ID slugs come from a shared `model_list_transform` (framework-aware filtering).
The Globus OAuth token helper (`scripts/alcf-token.py`) still lives in llm-rosetta.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-alcf
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `alcf--*` shims automatically.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.13.0` (needs the plugin shim loader)
- `ALCF_API_KEY` in the environment at request time

## License

MIT — see [LICENSE](LICENSE).
