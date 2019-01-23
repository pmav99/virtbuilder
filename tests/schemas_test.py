import pytest
from schema import SchemaError

from virtbuilder.schemas import definition_schema
from virtbuilder.utils import load_yaml


def test_valid_schema(yaml_loader):
    data = yaml_loader("valid.yml")
    definition_schema.validate(data)


class TestBuildSchema(object):
    @pytest.mark.parametrize("required_key", ["os", "version", "size", "format"])
    def test_required_keys(self, yaml_loader, required_key):
        data = yaml_loader("valid.yml")
        definition_schema.validate(data)
        del data["build"][required_key]
        with pytest.raises(SchemaError) as exc:
            definition_schema.validate(data)
        assert required_key in f"Missing {exc.value.code} key"

    @pytest.mark.parametrize(
        "optional_key", ["output", "arch", "no-sync", "memsize", "smp"]
    )
    def test_optional_keys(self, yaml_loader, optional_key):
        data = yaml_loader("valid.yml")
        definition_schema.validate(data)
        del data["build"][optional_key]
        assert definition_schema.validate(data)


class TestConfigSchema(object):
    @pytest.mark.parametrize(
        "optional_key",
        [
            "update",
            "selinux-relabel",
            "hostname",
            "timezone",
            "password-crypto",
            "provision",
        ],
    )
    def test_optional_keys(self, yaml_loader, optional_key):
        data = yaml_loader("valid.yml")
        definition_schema.validate(data)
        del data["build"]["config"][optional_key]
        assert definition_schema.validate(data)


class TestProvisionSchema(object):
    def test_provision_accepts_duplicate_keys(self, yaml_loader):
        data = yaml_loader("valid.yml")
        data["build"]["config"]["provision"] = [
            {"append-line": "/etc/hosts:127.0.0.1 localhost"},
            {"append-line": "/etc/hosts:127.0.1.2 localhost"},
        ]
        assert definition_schema.validate(data)
