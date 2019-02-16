import pytest

from pprint import pprint as pp
from virtbuilder import api


@pytest.mark.parametrize("fixture_filename", ["valid.yml", "minimum.yml"])
def test_validate(get_fixture, fixture_filename):
    input_file = get_fixture(fixture_filename)
    api.validate(input_file)


@pytest.mark.parametrize("fixture", ["minimum.yml", "valid.yml"])
def test_get_create_commands__no_stage(get_fixture, fixture):
    input_file = get_fixture(fixture)
    cmds = api.get_create_commands(input_file)
    assert len(cmds) == 4
    assert cmds[0].startswith("virt-builder")
    assert cmds[1].startswith("virsh")
    assert "vol-create" in cmds[1]
    assert cmds[2].startswith("virsh")
    assert "vol-upload" in cmds[2]
    assert cmds[-1].startswith("virt-install")


@pytest.mark.parametrize("fixture", ["minimum.yml", "valid.yml"])
@pytest.mark.parametrize("stage", api.CREATE_STAGES)
def test_get_create_commands__stage(get_fixture, fixture, stage):
    input_file = get_fixture(fixture)
    cmds = api.get_create_commands(input_file, stage)
    assert len(cmds) == 1


@pytest.mark.parametrize(
    "fixture, expected",
    [
        (
            "minimum.yml",
            [
                """virt-builder \\""",
                """  ubuntu-18.04 \\""",
                """  --format qcow2 \\""",
                """  --output kmaster.qcow2 \\""",
                """  --hostname kmaster \\""",
                """  --size "12G" """.rstrip(),
            ],
        ),
        (
            "valid.yml",
            [
                """virt-builder \\""",
                """  ubuntu-18.04 \\""",
                """  --verbose \\""",
                """  --format qcow2 \\""",
                """  --output kmaster.qcow2 \\""",
                """  --hostname kmaster \\""",
                """  --size "12G" \\""",
                """  --arch "x86_64" \\""",
                """  --no-sync \\""",
                """  --memsize "2000" \\""",
                """  --smp "2" \\""",
                """  --update \\""",
                """  --timezone "Europe/Athens" \\""",
                """  --password-crypto "sha512" \\""",
                """  --root-password "file:/home/feanor/Prog/git/virtbuilder/virtbuilder/root_password.txt" \\""",
                """  --firstboot-command "dpkg-reconfigure openssh-server" \\""",
                """  --ssh-inject "root:file:/home/feanor/.ssh/id_rsa.pub" \\""",
                """  --touch "/etc/apt/apt.conf.d/01norecommend" \\""",
                """  --append-line "/etc/apt/apt.conf.d/01norecommend:APT::Install-Recommends "0";" \\""",
                """  --append-line "/etc/apt/apt.conf.d/01norecommend:APT::Install-Suggests "0";" \\""",
                """  --install "net-tools,wget,curl,tree,ncdu,dfc,zsh,silversearcher-ag" """.rstrip(),
            ],
        ),
    ],
)
def test_create_image_cmd(load_fixture, fixture, expected):
    data = load_fixture(fixture)
    cmd = api.create_image_cmd(data, singleline=False)
    assert cmd == "\n".join(expected)
