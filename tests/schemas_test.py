import pytest
from schema import SchemaError

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
        assert f"Wrong key '{GIBBERISH}'" in str(exc.value)

    def _test_missing_mandatory_key_raises(self, key):
        data = self.valid.copy()
        data.pop(key)
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Missing key: '{key}'" in str(exc)

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
        "domain": "foo.local",
        "format": "qcow2",
        "os-variant": "ubuntu18.04",
        "os-name": "ubuntu",
        "os-version": "18.04",
        "verbose": True,
    }

    mandatory_keys = ["uri", "pool", "name", "format", "os-name", "os-version"]

    optional_keys = ["domain", "os-variant", "verbose"]

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

    @pytest.mark.parametrize("key", mandatory_keys)
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


class TestProvisionSchema(BaseSchemaTestCase):

    schema = schemas.ProvisionSchema
    valid = [
        {"append-line": "/etc/hosts:10.0.0.1 foo"},
        {"chmod": "0700:/path/p1"},
        {"copy": "remote_src:remote_dest"},
        {"copy-in": "local_src:remote_dest"},
        {"delete": "/path/deleteme"},
        {"edit": "/path/deleteme"},
        {"firstboot-command": "echo 1"},
        {"firstboot-install": ["pkg1", "pkg2"]},
        {"install": ["ansible", "apt", "wget"]},
        {"link": "target1:link1"},
        {"mkdir": "/path/makeme2"},
        {"move": "remote_src:remote_dest"},
        {"password": "asdf"},
        {"run": "/etc/fstab"},
        {"run-command": "/etc/fstab"},
        {"scrub": "root:/"},
        {"ssh-inject": "root:file:$HOME/.ssh/id_rsa.pub"},
        {"touch": "root:/"},
        {"truncate-recursive": "root:/"},
        {"uninstall": ["ansible", "apt", "wget"]},
        {"upload": "root:/"},
        {"write": "asdfasdf"},
    ]

    mandatory_keys = []
    optional_keys = [
        "append-line",
        "chmod",
        "copy",
        "copy-in",
        "delete",
        "edit",
        "firstboot",
        "firstboot-command",
        "firstboot-install",
        "install",
        "link",
        "mkdir",
        "move",
        "password",
        "run",
        "run_command",
        "scrub",
        "ssh-inject",
        "touch",
        "truncate-recursive",
        "uninstall",
        "upload",
        "write",
    ]

    def test_empty_schema_passes(self):
        self.schema.validate([])

    def test_duplicate_key_passes(self, load_fixture):
        data = [
            {"append-line": "/etc/hosts:127.0.0.1 localhost"},
            {"append-line": "/etc/hosts:127.0.1.2 localhost"},
        ]
        self.schema.validate(data)

    def test_extra_key_raises(self):
        data = self.valid.copy()
        data.append({GIBBERISH: GIBBERISH})
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Wrong key '{GIBBERISH}'" in str(exc.value)

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)
        data = self.valid.copy()
        data.pop(key)
        with pytest.raises(SchemaError) as exc:
            self.schema.validate(data)
        assert f"Missing key: '{key}'" in str(exc)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        data = self.valid.copy()
        for i, elem in enumerate(data):
            print(elem)
            if key == list(elem.keys())[0]:
                data.remove(elem)
                break
        self.schema.validate(data)


class TestImageConfigSchema(BaseSchemaTestCase):

    schema = schemas.ImageConfigSchema
    valid = {
        "update": True,
        "selinux-relabel": False,
        "timezone": "Europe/Athens",
        "password-crypto": "sha512",
        "root-password": "disabled",
        "provision": [
            {"append-line": "/etc/hosts:10.0.0.1 foo"},
            {"chmod": "0700:/path/p1"},
            {"install": ["wget", "curl"]},
        ],
    }

    mandatory_keys = []
    optional_keys = [
        "update",
        "selinux-relabel",
        "timezone",
        "password-crypto",
        "root-password",
        "provision",
    ]

    def test_empty_schema_passes(self):
        self.schema.validate({})

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        self._test_missing_optional_key_passes(key)


class TestImageSchema(BaseSchemaTestCase):
    schema = schemas.ImageSchema

    valid = {
        "size": "12G",
        "arch": "x86_64",
        "no-sync": True,
        "memsize": 2000,
        "smp": 2,
        "config": {
            "update": True,
            "selinux-relabel": False,
            "timezone": "Europe/Athens",
            "password-crypto": "sha512",
            "root-password": "disabled",
            "provision": [
                {"append-line": "/etc/hosts:10.0.0.1 foo"},
                {"chmod": "0700:/path/p1"},
                {"install": ["wget", "curl"]},
            ],
        },
    }

    mandatory_keys = ["size"]
    optional_keys = ["arch", "no-sync", "memsize", "smp", "config"]

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        self._test_missing_optional_key_passes(key)


class TestFullSchema(BaseSchemaTestCase):
    schema = schemas.FullSchema
    valid = {
        "general": {
            "uri": "qemu:///system",
            "pool": "kvm",
            "name": "kmaster",
            "format": "qcow2",
            "os-name": "ubuntu",
            "os-version": "18.04",
            "verbose": True,
        },
        "image": {"size": "10GB"},
        "vm": {"ram": 2000, "vcpus": 4},
    }
    mandatory_keys = ["general", "image", "vm"]
    optional_keys = []

    @pytest.mark.parametrize("key", mandatory_keys)
    def test_missing_mandatory_key_raises(self, key):
        self._test_missing_mandatory_key_raises(key)

    @pytest.mark.parametrize("key", optional_keys)
    def test_missing_optional_key_passes(self, key):
        self._test_missing_optional_key_passes(key)
