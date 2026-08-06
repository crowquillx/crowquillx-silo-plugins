#!/usr/bin/env python3

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable

SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[.-][0-9A-Za-z.-]+)?$")


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "crowquillx-silo-plugins"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def load_sources(path: Path) -> list[dict[str, str]]:
    document = json.loads(path.read_text())
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources.json must contain a non-empty sources array")
    required = {"plugin_id", "repo_url", "index_url"}
    result: list[dict[str, str]] = []
    for source in sources:
        if not isinstance(source, dict) or set(source) != required:
            raise ValueError(f"source must contain exactly {sorted(required)}")
        if not all(isinstance(source[key], str) and source[key] for key in required):
            raise ValueError("source fields must be non-empty strings")
        if not source["repo_url"].startswith("https://github.com/"):
            raise ValueError(f"unsupported repository URL for {source['plugin_id']}")
        if not source["index_url"].startswith(source["repo_url"] + "/releases/"):
            raise ValueError(f"index URL is outside {source['repo_url']}")
        result.append(source)
    return result


def validate_entry(entry: Any, source: dict[str, str]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError(f"catalog entry for {source['plugin_id']} is not an object")
    manifest = entry.get("manifest")
    binaries = entry.get("binaries")
    if not isinstance(manifest, dict) or not isinstance(binaries, dict):
        raise ValueError(f"catalog entry for {source['plugin_id']} lacks manifest or binaries")
    if manifest.get("plugin_id") != source["plugin_id"]:
        raise ValueError(f"source returned unexpected plugin ID {manifest.get('plugin_id')!r}")
    if entry.get("repo_url") != source["repo_url"]:
        raise ValueError(f"repository URL mismatch for {source['plugin_id']}")
    version = manifest.get("version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError(f"invalid version for {source['plugin_id']}")
    if manifest.get("silo_api_version") != "v1":
        raise ValueError(f"unsupported Silo API version for {source['plugin_id']}")

    platforms = manifest.get("supported_platforms")
    if not isinstance(platforms, list) or not platforms:
        raise ValueError(f"no supported platforms for {source['plugin_id']}")
    platform_keys: set[str] = set()
    for platform in platforms:
        if not isinstance(platform, dict) or not isinstance(platform.get("os"), str) or not isinstance(platform.get("arch"), str):
            raise ValueError(f"invalid supported platform for {source['plugin_id']}")
        platform_keys.add(f"{platform['os']}/{platform['arch']}")
    if platform_keys != set(binaries):
        raise ValueError(f"binary platforms do not match manifest for {source['plugin_id']}")

    release_prefix = source["repo_url"] + "/releases/download/"
    for platform, binary in binaries.items():
        if not isinstance(binary, dict):
            raise ValueError(f"invalid binary for {source['plugin_id']} {platform}")
        url = binary.get("url")
        checksum = binary.get("checksum")
        if not isinstance(url, str) or not url.startswith(release_prefix):
            raise ValueError(f"binary URL is outside {source['repo_url']} for {platform}")
        if not isinstance(checksum, str) or not SHA256.fullmatch(checksum):
            raise ValueError(f"invalid binary checksum for {source['plugin_id']} {platform}")
    return entry


def aggregate(sources: list[dict[str, str]], fetcher: Callable[[str], dict[str, Any]] = fetch_json) -> dict[str, Any]:
    plugins: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in sources:
        plugin_id = source["plugin_id"]
        if plugin_id in seen:
            raise ValueError(f"duplicate configured plugin ID {plugin_id}")
        source_index = fetcher(source["index_url"])
        entries = source_index.get("plugins") if isinstance(source_index, dict) else None
        if not isinstance(entries, list):
            raise ValueError(f"source index for {plugin_id} lacks a plugins array")
        matches = [
            entry
            for entry in entries
            if isinstance(entry, dict)
            and isinstance(entry.get("manifest"), dict)
            and entry["manifest"].get("plugin_id") == plugin_id
        ]
        if len(matches) != 1:
            raise ValueError(f"source index for {plugin_id} must contain exactly one matching entry")
        plugins.append(validate_entry(matches[0], source))
        seen.add(plugin_id)
    plugins.sort(key=lambda entry: entry["manifest"]["plugin_id"])
    return {"plugins": plugins}


def render_catalog(sources_path: Path) -> str:
    catalog = aggregate(load_sources(sources_path))
    return json.dumps(catalog, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate trusted Silo plugin repository indexes")
    parser.add_argument("--sources", type=Path, default=Path("sources.json"))
    parser.add_argument("--output", type=Path, default=Path("repository.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        rendered = render_catalog(args.sources)
        if args.check:
            if not args.output.exists() or args.output.read_text() != rendered:
                print(f"{args.output} is not current", file=sys.stderr)
                return 1
        else:
            args.output.write_text(rendered)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
