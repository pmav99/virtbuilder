import pytest
from schema import SchemaError, SchemaMissingKeyError

import virtbuilder.schemas as schemas
from virtbuilder.utils import load_yaml


class TestBuildConfigProvisionSchema(object):
    @property
    def schema(self):
        return schemas.build_config_provision_schema

    def test_valid_schema_passes(self, load_fixture):
        data = load_fixture("valid.yml")
        self.schema.validate(data["build"]["config"]["provision"])

    def test_empty_schema_passes(self):
        self.schema.validate([])

    def test_duplicate_key_passes(self, load_fixture):
        data = [
            {"append-line": "/etc/hosts:127.0.0.1 localhost"},
            {"append-line": "/etc/hosts:127.0.1.2 localhost"},
        ]
        self.schema.validate(data)


class TestBuildConfigSchema(object):
    @property
    def schema(self):
        return schemas.build_config_schema

    def test_valid_schema_passes(self, load_fixture):
        data = load_fixture("valid.yml")
        self.schema.validate(data["build"]["config"])

    def test_empty_schema_passes(self):
        self.schema.validate({})

    @pytest.mark.parametrize(
        "optional_key",
        [
            "update",
            "selinux-relabel",
            "hostname",
            "timezone",
            "root-password",
            "password-crypto",
            "provision",
        ],
    )
    def test_missing_optional_key_passes(self, load_fixture, optional_key):
        data = load_fixture("valid.yml")["build"]["config"]
        del data[optional_key]
        self.schema.validate(data)


class TestBuildSchema(object):
    @property
    def schema(self):
        return schemas.build_schema

    def test_valid_schema_passes(self, load_fixture):
        data = load_fixture("valid.yml")
        self.schema.validate(data["build"])

    def test_empty_schema_raises(self):
        print(type(self.schema))
        with pytest.raises(SchemaMissingKeyError) as exc:
            self.schema.validate({})
        # Check that the mandatory fields are mentioned in the traceback
        exc_code = exc.value.code
        assert "os" in exc_code
        assert "version" in exc_code
        assert "size" in exc_code
        assert "format" in exc_code

    @pytest.mark.parametrize("required_key", ["os", "version", "size", "format"])
    def test_missing_required_key_raises(self, load_fixture, required_key):
        data = load_fixture("valid.yml")
        del data["build"][required_key]
        with pytest.raises(SchemaError) as exc:
            schemas.definition_schema.validate(data)
        assert required_key in f"Missing {exc.value.code} key"

    @pytest.mark.parametrize(
        "optional_key", ["output", "arch", "no-sync", "memsize", "smp"]
    )
    def test_missing_optional_key_passes(self, load_fixture, optional_key):
        data = load_fixture("valid.yml")
        schemas.definition_schema.validate(data)
        del data["build"][optional_key]
        assert schemas.definition_schema.validate(data)
