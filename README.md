# llm-rosetta-shim-alcf

ALCF (Argonne Leadership Computing Facility) provider shims for
[llm-rosetta](https://github.com/Oaklight/llm-rosetta), delivered as a **plugin
package** rather than as built-in shims.

The `alcf_*` shims left llm-rosetta core in 0.14.0
([#666](https://github.com/Oaklight/llm-rosetta/issues/666)); this package is now
their only source. Declare it in the gateway config and existing provider
entries keep their names:

```jsonc
{ "shims": { "presets": ["alcf"] } }
```

`shims.presets` expands to this repository's archive path via llm-rosetta's
catalogue; the equivalent explicit entry is `{"url": "...", "path":
"src/llm_rosetta_shim_alcf/providers"}`. The repository is public, so no
`token_env` is needed.

## Shims

The names follow the parent's canonical `alcf_<cluster>--<format>` spelling: the
cluster sits in the provider segment and the segment after `--` is always the API
format. All three clusters declare `group: alcf`, so the admin provider picker
shows a single `alcf` top level whose rows read `metis · chat_completions`,
`minerva · chat_completions` and `sophia · chat_completions`.

| Shim | Base | Endpoint |
|:---|:---|:---|
| `alcf_metis--chat_completions` | `chat_completions` | `https://inference-api.alcf.anl.gov/resource_server/metis/api/v1` |
| `alcf_minerva--chat_completions` | `chat_completions` | `https://inference-api.alcf.anl.gov/resource_server/minerva/api/v1` |
| `alcf_sophia--chat_completions` | `chat_completions` | `https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1` |

The pre-rename spellings (`alcf--metis`, `alcf--minerva`, `alcf--sophia`) no
longer resolve; use the canonical names above.

Model ID slugs come from a shared `model_list_transform` (framework-aware filtering).
The Globus OAuth token helper (`scripts/alcf-token.py`) still lives in llm-rosetta.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-alcf
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `alcf_<cluster>--chat_completions` shims automatically.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.13.0` (needs the plugin shim loader)
- `ALCF_API_KEY` in the environment at request time

## License

MIT — see [LICENSE](LICENSE).
