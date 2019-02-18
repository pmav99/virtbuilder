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
        "os-variant": Regex(r"\w+"),
        "os-name": Regex(r"\w+"),
        "os-version": Regex(r"\w+"),
        Optional("verbose"): bool,
    }
)

VM_Schema = Schema(
    {
        "ram": And(Use(int), lambda n: n > 0),
        "vcpus": And(Use(int), lambda n: n > 0),
        Optional("graphics"): And(str, len),
        Optional("console"): And(str, len),
        Optional("extra-args"): And(str, len),
        Optional("disk"): And(str, len),
        Optional("network"): And(str, len),
    }
)


# Provision is a
ProvisionSchema = Schema(
    [
        {Optional("append-line"): And(str, len)},
        {Optional("chmod"): And(str, len)},
        {Optional("copy"): And(str, len)},
        {Optional("copy-in"): And(str, len)},
        {Optional("delete"): And(str, len)},
        {Optional("edit"): And(str, len)},
        {Optional("firstboot"): And(str, len)},
        {Optional("firstboot-command"): And(str, len)},
        {Optional("firstboot-install"): [And(str, len)]},
        {Optional("install"): [And(str, len)]},
        {Optional("link"): And(str, len)},
        {Optional("mkdir"): And(str, len)},
        {Optional("move"): And(str, len)},
        {Optional("password"): And(str, len)},
        {Optional("run"): And(str, len, Use(pathlib.Path), lambda p: p.exists())},
        {Optional("run-command"): And(str, len)},
        {Optional("scrub"): And(str, len)},
        {Optional("ssh-inject"): And(str, len)},
        {Optional("touch"): And(str, len)},
        {Optional("truncate-recursive"): And(str, len)},
        {Optional("uninstall"): [And(str, len)]},
        {Optional("upload"): And(str, len)},
        {Optional("write"): And(str, len)},
    ]
)

ImageConfigSchema = Schema(
    {
        Optional("update"): And(bool),
        Optional("selinux-relabel"): And(bool),
        Optional("timezone"): And(str, len),
        Optional("password-crypto", default="sha512"): And(
            str, len, OneOf("md5", "sha256", "sha512")
        ),
        Optional("root-password"): And(str, len),
        Optional("provision"): ProvisionSchema,
    }
)

ImageSchema = Schema(
    {
        "size": And(str, len),
        Optional("arch"): And(str, len),
        Optional("no-sync"): And(bool),
        Optional("memsize"): And(int, lambda n: n > 1000),
        Optional("smp", default=4): And(int, lambda n: n > 1),
        # TODO Add support for --attach and --attach-format
        Optional("config"): ImageConfigSchema,
    }
)

FullSchema = Schema({"general": GeneralSchema, "image": ImageSchema, "vm": VM_Schema})

full_schema = FullSchema
