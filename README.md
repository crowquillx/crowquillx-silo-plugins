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
| [Theme Songs](https://github.com/crowquillx/silo-theme-songs) | Downloads movie and series themes as MP3. |
| [AnimeThemes](https://github.com/crowquillx/silo-anime-themes) | Downloads anime opening and ending themes as MP3. |
| [AniList Sync](https://github.com/crowquillx/silo-anilist-sync) | Syncs anime watch history with AniList. |
| [ShokoAnime VFS](https://github.com/crowquillx/silo-shoko-plugin) | Builds a Shoko media library with metadata and artwork. |
| [Comic Pages](https://github.com/crowquillx/silo-comic-pages) | Serves comic pages to the Silo Aidoku source. |

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
