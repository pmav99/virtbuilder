import pytest
from schema import SchemaError, SchemaMissingKeyError

import virtbuilder.schemas as schemas
from virtbuilder.utils import load_yaml


GIBBERISH = "gibberish"


class BaseSchemaTestCase(object):

    schema = None
    valid = {}
    mandatory_keys = []
    optional_keys = []

    def test_valid_schema_passes(self):
        self.schema.validate(self.valid)

    def test_extra_key_raises(self):
        data = self.valid.copy()
        data[GIBBERISH] = GIBBERISH
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Wrong keys '{GIBBERISH}'" in str(exc.value)

    def _test_missing_mandatory_key_raises(self, key):
        data = self.valid.copy()
        data.pop(key)
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Missing keys: '{key}'" in str(exc)

    def _test_missing_optional_key_passes(self, key):
        data = self.valid.copy()
        data.pop(key)
        self.schema.validate(data)


class TestGeneralSchema(BaseSchemaTestCase):

    schema = schemas.GeneralSchema

    valid = {
        "uri": "qemu:///system",
        "pool": "kvm",
        "name": "kmaster",
        "format": "qcow2",
        "os-type": "linux",
        "os-name": "ubuntu",
        "os-version": "18.04",
    }

    mandatory_keys = valid.keys()

    optional_keys = []

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        self._test_missing_optional_key_passes(key)

    def test_non_uri_raises(self):
        data = self.valid.copy()
        data["uri"] = GIBBERISH
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Key 'uri' error:" in str(exc.value)
        assert "Regex" in str(exc.value)
        assert GIBBERISH in str(exc.value)

    def test_unknown_image_format_raises(self):
        data = self.valid.copy()
        data["format"] = GIBBERISH
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Key 'format' error:" in str(exc.value)
        assert GIBBERISH in str(exc.value)

    @pytest.mark.parametrize("key", valid.keys())
    def test_empty_string_raises(self, key):
        data = self.valid.copy()
        data[key] = ""
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Key '{key}' error:" in str(exc.value)
        assert "Regex" in str(exc.value)


class TestVM_Schema(BaseSchemaTestCase):

    schema = schemas.VM_Schema

    valid = {
        "ram": 3072,
        "vcpus": 3,
        "graphics": "None",
        "console": "pty,target_type=serial",
        "extra-args": "console=ttyS0",
        "disk": "vol=kvm/kmaster,bus=virtio,cache=none,io=native",
        "network": "bridge=virbr2,mac=52:54:00:10:00:10",
    }

    mandatory_keys = ["ram", "vcpus"]

    optional_keys = ["graphics", "console", "extra-args", "disk", "network"]

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        self._test_missing_optional_key_passes(key)

    @pytest.mark.parametrize("value", ["asdf", "-32"])
    def test_non_positive_ram_raises(self, value):
        data = self.valid.copy()
        data["ram"] = value
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert "Key 'ram' error" in str(exc.value)

    @pytest.mark.parametrize("value", ["asdf", "-32"])
    def test_non_positive_vcpus_raises(self, value):
        data = self.valid.copy()
        data["vcpus"] = value
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert "Key 'vcpus' error" in str(exc.value)


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
        assert "format" in exc_code

    @pytest.mark.parametrize("required_key", ["os", "version", "format"])
    def test_missing_required_key_raises(self, load_fixture, required_key):
        data = load_fixture("valid.yml")
        del data["build"][required_key]
        with pytest.raises(SchemaError) as exc:
            schemas.full_schema.validate(data)
        assert required_key in f"Missing {exc.value.code} key"

    @pytest.mark.parametrize(
        "optional_key", ["output", "arch", "no-sync", "size", "memsize", "smp"]
    )
    def test_missing_optional_key_passes(self, load_fixture, optional_key):
        data = load_fixture("valid.yml")
        schemas.full_schema.validate(data)
        del data["build"][optional_key]
        assert schemas.full_schema.validate(data)
