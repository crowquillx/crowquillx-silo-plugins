import copy
import unittest

from scripts.update_catalog import aggregate, validate_entry


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

    def test_rejects_duplicate_configured_plugin(self):
        with self.assertRaisesRegex(ValueError, "duplicate configured plugin ID"):
            aggregate([self.source, self.source], lambda _: {"plugins": [self.entry]})


if __name__ == "__main__":
    unittest.main()
