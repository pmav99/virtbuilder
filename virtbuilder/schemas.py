import pathlib
from schema import Schema, And, Or, Use, Optional, SchemaError, Regex


def OneOf(*unique):
    def one_of(value):
        return value in set(unique)

    return one_of


GeneralSchema = Schema(
    {
        "uri": Regex(r"\w+:(\/?\/?)[^\s]+"),
        "pool": Regex(r"\w+"),
        "name": Regex(r"\w+"),
        "format": And(Regex(r"\w+"), lambda s: s in ("qcow2", "raw")),
        "os-type": Regex(r"\w+"),
        "os-name": Regex(r"\w+"),
        "os-version": Regex(r"\w+"),
    }
)

# Provision is a
build_config_provision_schema = Schema(
    [
        Optional(
            Or(
                {"append-line": And(str, len)},
                {"chmod": And(str, len)},
                {"copy": And(str, len)},
                {"copy-in": And(str, len)},
                {"delete": And(str, len)},
                {"edit": And(str, len)},
                {"firstboot": And(str, len)},
                {"firstboot-command": And(str, len)},
                {"firstboot-install": [And(str, len)]},
                {"install": [And(str, len)]},
                {"link": And(str, len)},
                {"mkdir": And(str, len)},
                {"move": And(str, len)},
                {"password": And(str, len)},
                {"run": And(str, len, Use(pathlib.Path), lambda p: p.exists())},
                {"run-command": And(str, len)},
                {"scrub": And(str, len)},
                {"ssh-inject": And(str, len)},
                {"touch": And(str, len)},
                {"touch": And(str, len)},
                {"truncate-recursive": And(str, len)},
                {"uninstall": [And(str, len)]},
                {"upload": And(str, len)},
                {"write": And(str, len)},
            )
        )
    ]
)

build_config_schema = Schema(
    {
        Optional("update"): And(bool),
        Optional("selinux-relabel"): And(bool),
        Optional("hostname"): And(str, len),
        Optional("timezone"): And(str, len),
        Optional("password-crypto", default="sha512"): And(
            str, len, OneOf("md5", "sha256", "sha512")
        ),
        Optional("root-password"): And(str, len),
        Optional("provision"): build_config_provision_schema,
    }
)

build_schema = Schema(
    {
        "os": And(Use(str), len),
        "version": And(str, len),
        Optional("output"): And(str, len),
        Optional("size"): And(str, len),
        "format": And(str, len, OneOf("raw", "qcow2")),
        Optional("arch"): And(str, len),
        Optional("no-sync"): And(bool),
        Optional("memsize"): And(int, lambda n: n > 1000),
        Optional("smp", default=4): And(int, lambda n: n > 1),
        # TODO Add support for --attach and --attach-format
        Optional("config"): build_config_schema,
    }
)

pool_schema = Schema(
    {
        "uri": And(str, len),
        "pool": And(str, len),
        "volume": And(str, len),
        Optional("image"): And(str, len),
    }
)

vm_schema = Schema({})

full_schema = Schema(
    {
        Optional("build"): build_schema,
        Optional("pool"): pool_schema,
        Optional("vm"): vm_schema,
    }
)
