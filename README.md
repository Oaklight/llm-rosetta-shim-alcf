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
The Globus OAuth exchange ships **with this package**. The vendor manifest
`providers/alcf/provider.yaml` declares the credential once for all three
clusters — `connection.api_key_env: ALCF_API_KEY` and
`connection.token_command: [python3, token.py]`, resolved against the manifest's
own directory — and every leaf inherits it. Log in once, and the gateway runs the
exchange at startup, on the declared interval and after an upstream 401. A
provider that names its own `token_command` still wins.

```bash
python3 -m llm_rosetta_shim_alcf.providers.alcf.token --login   # once, per user
```

The same module takes `--status` for the token's expiry and `--probe metis` to
check it against a cluster.

## Install

```bash
pip install llm-rosetta llm-rosetta-shim-alcf
```

llm-rosetta discovers the `llm_rosetta.shim_providers` entry point and registers
the `alcf_<cluster>--chat_completions` shims automatically.

## Archive and mirror

Every release publishes one archive of the bundled shims, so a gateway can load
them from a host other than GitHub. `main` never carries it: `dist/` is build
output and is in `.gitignore`.

- `v<version>/alcf.tar.gz` and `v<version>/alcf.tar.gz.sha256` live on the
  orphan `dist` branch.
- The same bytes are attached to the GitHub Release, with the digest in its
  notes.

Two interchangeable, version-pinned URLs for the same bytes:

```
https://github.com/Oaklight/llm-rosetta-shim-alcf/releases/download/v<version>/alcf.tar.gz
https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-alcf@dist/v<version>/alcf.tar.gz
```

The archive's root is `providers/`, the layout the package ships under
`src/llm_rosetta_shim_alcf/providers`, so a gateway source declares `path: "providers"`:

```jsonc
{
  "shims": {
    "remotes": [
      {
        "url": "https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-alcf@dist/v<version>/alcf.tar.gz",
        "path": "providers",
        "archive": "tar.gz",
        "sha256": "<digest from v<version>/alcf.tar.gz.sha256>"
      }
    ]
  }
}
```

The digest is what pins the mirror, and the same value appears in the release
notes. jsDelivr is only the default suggestion: the gateway accepts any URL that
serves the same bytes, an internal mirror included.

### Publishing a release

1. Bump `__version__` in `src/llm_rosetta_shim_alcf/__init__.py`. The tag must match it —
   the release workflow passes the tag without its `v` as `--expect-version` and
   refuses a mismatch.
2. `python scripts/build_shim_archive.py --write` builds
   `dist/v<version>/alcf.tar.gz` and its digest locally and verifies the
   layout. CI runs the same build without writing on every push, so a tree whose
   `providers/` layout changed fails before a tag is cut.
3. Tag and push: `git tag v<version> && git push origin v<version>`.
4. `.github/workflows/release.yml` builds from the tag, creates or updates the
   GitHub Release, uploads the archive and its digest file, and commits
   `v<version>/` to the `dist` branch.

The workflow requests `contents: write` for `GITHUB_TOKEN`, because it creates
the release and pushes `dist`. An organization that downgrades action tokens to
read-only must restore "Read and write permissions" under Settings → Actions →
General, or the release step fails.

## Requirements

- Python >= 3.10
- `llm-rosetta >= 0.14.0.dev28` (the plugin shim loader, the vendor manifest and
  `connection.token_command`; an older core reads the manifest as a shim and the
  provider would start with no credential)
- No credential in the environment: the shipped exchange mints the token from
  `~/.globus` (or `--token-file` / `--tokens-dir`)

## License

MIT — see [LICENSE](LICENSE).
