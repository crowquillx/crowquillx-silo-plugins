# Crowquillx Silo Plugins

A catalog of Silo plugins maintained by [crowquillx](https://github.com/crowquillx).

## Install

1. Open **Administration → Plugins → Catalog** in Silo.
2. Under **Repositories**, select **Add** and enter this URL:

```text
https://raw.githubusercontent.com/crowquillx/crowquillx-silo-plugins/main/repository.json
```

3. Install a plugin from the catalog. Open its settings under **Installed** and follow the setup instructions in its README.

| Plugin | What it does |
| --- | --- |
| [Theme Songs](https://github.com/crowquillx/silo-theme-songs) | Downloads movie and series themes, and anime openings and endings, as MP3. |
| [AniList Sync](https://github.com/crowquillx/silo-anilist-sync) | Syncs anime watch history with AniList. |
| [ShokoAnime VFS](https://github.com/crowquillx/silo-shoko-plugin) | Builds a library from your Shoko groups, with metadata, artwork and theme songs. |

### Deprecated

These plugins are no longer maintained and may not work with current Silo releases. Their repositories are archived, and they will be removed from the catalog later. Existing installations keep running, but get no fixes or updates.

| Plugin | What it did |
| --- | --- |
| [Comic Pages](https://github.com/crowquillx/silo-comic-pages) | Serves comic pages to the Silo Aidoku source. |
| [Light Novel Metadata](https://github.com/crowquillx/silo-light-novel-metadata) | Matches light novel volumes to RanobeDB and adds high-resolution covers. |

## Build

Requires Python 3. Plugin sources are listed in `sources.json`.

```sh
python3 -m unittest discover -s tests
python3 scripts/update_catalog.py
```

The output is `repository.json`. The catalog workflow also checks for plugin releases every 15 minutes.

## Acknowledgments

- [Silo Server](https://github.com/Silo-Server/silo-server) for the plugin platform.

[MIT license](LICENSE).
