# Crowquillx Silo Plugins

An unofficial catalog of plugins for
[Silo Server](https://github.com/Silo-Server/silo-server) maintained by
[crowquillx](https://github.com/crowquillx). This repository is independent of
the Silo Server project and is not an official Silo catalog.

## Add the catalog to Silo

1. Sign in to Silo as an administrator.
2. Open **Administration → Plugins**.
3. Select the **Catalog** tab.
4. Under **Repositories**, select **Add**.
5. Enter a recognizable name such as `Crowquillx plugins`.
6. Enter this repository URL:

   ```text
   https://raw.githubusercontent.com/crowquillx/crowquillx-silo-plugins/main/repository.json
   ```

7. Select **Add**. The plugins below will appear in Silo's catalog.
8. Select **Install** on the desired plugin, then configure it from the
   **Installed** tab.

Silo installs the binary matching its operating system and architecture and
verifies the published SHA-256 checksum. Repository installations use Silo's
automatic update policy by default; administrators can select notification-only
or manual updates for an installation.

## Compatibility

AniList Sync `v0.3.x` requires a Silo build containing the plugin-backed watch
provider host added by
[Silo Server PR #475](https://github.com/Silo-Server/silo-server/pull/475).
Until a Silo release includes that host, use Silo Server from its current
`main` branch.

## Included plugins

| Plugin | Plugin ID | Description | Platforms |
| --- | --- | --- | --- |
| [AniList Sync](https://github.com/crowquillx/silo-anilist-sync) | `dev.crowquillx.anilist-sync` | Synchronizes completed anime playback and optional manual watched marks with AniList, and imports mapped AniList watch history. | Linux amd64, Linux arm64, macOS arm64 |
| [ShokoAnime VFS](https://github.com/crowquillx/silo-shoko-plugin) | `silo.shokoanime` | Builds a group-aware Shoko virtual filesystem and provides typed metadata and artwork to Silo. | Linux amd64, Linux arm64, macOS arm64 |

## How the catalog updates

`sources.json` lists each trusted plugin repository and its stable release
index. The catalog workflow checks those indexes every 15 minutes, validates
plugin identity, version, platform coverage, release URLs, and checksum format,
then updates `repository.json` only when content changes.

A plugin must publish a release-level `repository.json` containing its
manifest, platform binaries, and SHA-256 checksums before it can be added to
`sources.json`. Duplicate plugin IDs, mismatched repository URLs, missing
platform binaries, and invalid checksums are rejected.

## License

MIT. See [`LICENSE`](LICENSE).
