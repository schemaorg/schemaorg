# AGENTS.md

## Project overview

Schema.org is a Python application that combines the vocabulary source in `data/` with examples and documentation to build a static website in `software/site/`. The generated site is ignored by git and should not be edited directly.

Work from the repository root. The supported runtime is Python 3.11 or newer. Install the pinned dependencies before running the build scripts:

```sh
python -m pip install -r software/requirements.txt
```

## Project references

- Development and deployment details: [software/SOFTWARE_README.md](software/SOFTWARE_README.md)
- Developer-facing vocabulary downloads and formats: [docs/developers.html](docs/developers.html)
- Continuous integration build and tests: [.github/workflows/ci_tests.yml](.github/workflows/ci_tests.yml)
- Tag-triggered release job: [.github/workflows/create-release.yml](.github/workflows/create-release.yml)
- Scheduled stale issue and pull request maintenance: [.github/workflows/stale.yml](.github/workflows/stale.yml)

## Build and test

### In the devcontainer

The devcontainer runs the dependency installation from `postCreateCommand`. After opening the repository in the container, run these commands in the integrated terminal from the repository root; GitHub Actions is not required.

To reproduce the CI build preparation and tests locally:

```sh
./software/scripts/buildsite.py -e -f RDFExport.nquads Context Examples
version="$(./software/scripts/schemaversion.py)"
mkdir -p software/site/releases/LATEST
cp -r "software/site/releases/$version"/. software/site/releases/LATEST/
./software/scripts/buildsite.py -r --shacltests
```

For the complete local build and test pass, use:

```sh
./software/scripts/buildsite.py -a -r --shacltests
```

The release and stale workflows are GitHub-only automation. The release job runs for `v*` tags, while the stale job runs on its schedule; neither is needed to build or test the site in the devcontainer.

- Build the complete local site: `./software/scripts/buildsite.py -a`
- Run the repository tests and SHACL example validation: `./software/scripts/buildsite.py -a -r --shacltests`
- Run the CI-style test preparation, then tests:
  `software/scripts/buildsite.py -e -f RDFExport.nquads Context Examples`
  followed by `software/scripts/buildsite.py -r --shacltests`
- Rebuild static documentation and assets: `./software/scripts/buildsite.py -s`
- Rebuild all generated output files: `./software/scripts/buildsite.py -f All`
- Rebuild all dynamic documentation: `./software/scripts/buildsite.py -d All`
- Rebuild selected term pages: `./software/scripts/buildsite.py -t Book sameAs`
- Serve the generated site: `./software/scripts/devserv.py --host 0.0.0.0 --port 8080`

The complete build can take several minutes. Use targeted `-t`, `-d`, `-f`, or `-s` builds while iterating, and run `-a` before release or deployment. The devcontainer forwards port 8080.

## Source and generated files

- Vocabulary definitions live in Turtle files under `data/` and `data/ext/`.
- Example data lives in `*examples.txt` files under `data/` and `data/ext/`.
- Static source documentation lives under `docs/`; rebuild it with `-s` after changes.
- `versions.json` controls the schema version and release log. A version change requires a full build.
- Do not commit or hand-edit generated files under `software/site/`.

When editing `docs/developers.html` or another static page, preserve the existing template insertion markers and links used by the site builder. Keep browser-side behavior compatible with the generated page and verify the affected page through the local server when practical.

## Python conventions

Follow `software/CODE_README.md`: use type hints for functions, context managers for file operations, standard `logging` instead of prints, and grouped lexicographically sorted imports. Keep code platform-agnostic and avoid adding dependencies when the standard library is sufficient. Ruff is the recommended formatter and linter, although CI does not currently run it.

## GitHub Actions

The main CI workflow installs `software/requirements.txt`, prepares RDF exports, and runs the repository and SHACL tests. The release workflow runs only for `v*` tags; the stale workflow is scheduled maintenance. Keep local commands compatible with these workflows, and do not change release or automation behavior unless the task specifically requires it.
