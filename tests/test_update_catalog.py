import copy
import unittest

import json
import tempfile
from pathlib import Path

from scripts.update_catalog import aggregate, load_sources, validate_entry


class CatalogAggregationTests(unittest.TestCase):
    def setUp(self):
        self.source = {
            "plugin_id": "dev.example.one",
            "repo_url": "https://github.com/example/plugin-one",
            "index_url": "https://github.com/example/plugin-one/releases/latest/download/repository.json",
        }
        self.entry = {
            "manifest": {
                "plugin_id": "dev.example.one",
                "version": "1.2.3",
                "silo_api_version": "v1",
                "supported_platforms": [{"os": "linux", "arch": "amd64"}],
            },
            "repo_url": "https://github.com/example/plugin-one",
            "binaries": {
                "linux/amd64": {
                    "url": "https://github.com/example/plugin-one/releases/download/v1.2.3/plugin-linux-amd64",
                    "checksum": "a" * 64,
                }
            },
        }

    def test_aggregate_selects_configured_plugin(self):
        unrelated = copy.deepcopy(self.entry)
        unrelated["manifest"]["plugin_id"] = "dev.example.unrelated"
        catalog = aggregate([self.source], lambda _: {"plugins": [unrelated, self.entry]})
        self.assertEqual([self.entry], catalog["plugins"])

    def test_aggregate_combines_multiple_plugins_in_stable_order(self):
        second_source = {
            "plugin_id": "dev.example.two",
            "repo_url": "https://github.com/example/plugin-two",
            "index_url": "https://github.com/example/plugin-two/releases/latest/download/repository.json",
        }
        second_entry = copy.deepcopy(self.entry)
        second_entry["manifest"]["plugin_id"] = second_source["plugin_id"]
        second_entry["repo_url"] = second_source["repo_url"]
        second_entry["binaries"]["linux/amd64"]["url"] = (
            second_source["repo_url"] + "/releases/download/v1.2.3/plugin-linux-amd64"
        )
        responses = {
            self.source["index_url"]: {"plugins": [self.entry]},
            second_source["index_url"]: {"plugins": [second_entry]},
        }

        catalog = aggregate([second_source, self.source], responses.__getitem__)

        self.assertEqual(
            ["dev.example.one", "dev.example.two"],
            [entry["manifest"]["plugin_id"] for entry in catalog["plugins"]],
        )

    def test_marks_deprecated_plugin_in_catalog_text(self):
        entry = copy.deepcopy(self.entry)
        entry["manifest"]["presentation"] = {
            "display_name": "Plugin One",
            "summary": "Does things.",
            "description_markdown": "Details.",
            "setup_markdown": "Setup.",
        }
        source = {**self.source, "deprecated": "No longer maintained."}

        presentation = validate_entry(entry, source)["manifest"]["presentation"]

        self.assertEqual("Plugin One (Deprecated)", presentation["display_name"])
        self.assertEqual("Deprecated: No longer maintained.", presentation["summary"])
        self.assertEqual("**Deprecated.** No longer maintained.\n\nDetails.", presentation["description_markdown"])
        self.assertEqual("Setup.", presentation["setup_markdown"])
        self.assertEqual("Plugin One", entry["manifest"]["presentation"]["display_name"])

    def test_deprecation_without_presentation_uses_plugin_id(self):
        source = {**self.source, "deprecated": "Unsupported."}
        presentation = validate_entry(self.entry, source)["manifest"]["presentation"]
        self.assertEqual("dev.example.one (Deprecated)", presentation["display_name"])
        self.assertEqual("**Deprecated.** Unsupported.", presentation["description_markdown"])
        self.assertNotIn("presentation", self.entry["manifest"])

    def test_load_sources_accepts_deprecation_and_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.json"
            path.write_text(json.dumps({"sources": [{**self.source, "deprecated": "Unsupported."}]}))
            self.assertEqual("Unsupported.", load_sources(path)[0]["deprecated"])
            for extra in ({"deprecated": ""}, {"note": "x"}):
                path.write_text(json.dumps({"sources": [{**self.source, **extra}]}))
                with self.assertRaises(ValueError):
                    load_sources(path)

    def test_rejects_binary_platform_not_advertised_by_manifest(self):
        entry = copy.deepcopy(self.entry)
        entry["binaries"]["linux/arm64"] = copy.deepcopy(entry["binaries"]["linux/amd64"])
        with self.assertRaisesRegex(ValueError, "binary platforms do not match"):
            validate_entry(entry, self.source)

    def test_rejects_binary_from_another_repository(self):
        entry = copy.deepcopy(self.entry)
        entry["binaries"]["linux/amd64"]["url"] = "https://example.invalid/plugin"
        with self.assertRaisesRegex(ValueError, "binary URL is outside"):
            validate_entry(entry, self.source)

    def test_normalizes_runtime_form_enums_for_catalog_json(self):
        self.entry["manifest"]["global_config_schema"] = [{"admin_form": {"fields": [
            {"key": "token", "control": "ADMIN_FORM_CONTROL_PASSWORD", "secret": True},
            {"key": "enabled", "control": 5},
        ]}}]
        result = validate_entry(self.entry, self.source)
        fields = result["manifest"]["global_config_schema"][0]["admin_form"]["fields"]
        self.assertEqual(3, fields[0]["control"])
        self.assertTrue(fields[0]["secret"])
        self.assertEqual(5, fields[1]["control"])
        self.assertEqual("ADMIN_FORM_CONTROL_PASSWORD", self.entry["manifest"]["global_config_schema"][0]["admin_form"]["fields"][0]["control"])

    def test_rejects_unknown_symbolic_form_control(self):
        self.entry["manifest"]["user_config_schema"] = [{"admin_form": {"fields": [
            {"key": "bad", "control": "TYPO"},
        ]}}]
        with self.assertRaisesRegex(ValueError, "unknown admin form control"):
            validate_entry(self.entry, self.source)

    def test_rejects_duplicate_configured_plugin(self):
        with self.assertRaisesRegex(ValueError, "duplicate configured plugin ID"):
            aggregate([self.source, self.source], lambda _: {"plugins": [self.entry]})


if __name__ == "__main__":
    unittest.main()
