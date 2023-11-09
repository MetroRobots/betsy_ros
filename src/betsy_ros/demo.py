import click
from . import (get_ros_version, get_package_name_from_path, get_workspace_root,
               get_package_names, find_package, is_binary_ros, list_interfaces)


def main(argv=None):
    version, distro = get_ros_version()
    click.secho(f'ROS {version}: {distro}', bg='blue', fg='bright_white')

    build_type, root = get_workspace_root()
    click.secho(f'{build_type.name} workspace: {root}', bg='blue', fg='cyan')

    current = get_package_name_from_path()
    if current:
        click.secho(f'Currently in package {current}', fg='white', bg='blue')
    else:
        click.secho('Not currently in a package!', bg='blue', fg='black')

    pkgs = get_package_names(version)
    click.secho(f'Found {len(pkgs)} packages', fg='white', bg='blue')

    max_len = max(len(pkg) for pkg in pkgs)
    binary = []
    source = []

    for pkg in sorted(pkgs):
        path = find_package(pkg, version, str(root))
        if is_binary_ros(path):
            binary.append((pkg, path))
        else:
            source.append((pkg, path))

    fmt_s = '{pkg:' + str(max_len) + '} {path}'

    def print_partial_package_list(name, packages):
        if not packages:
            return
        click.secho()
        click.secho(f'{name} Packages', fg='bright_blue')
        if len(packages) <= 20:
            for pkg, path in packages:
                click.secho(fmt_s.format(pkg=pkg, path=path), fg='blue')
        else:
            for pkg, path in packages[:10]:
                click.secho(fmt_s.format(pkg=pkg, path=path), fg='blue')
            click.secho(f' ... and {len(packages) - 10} more', fg='blue')
    print_partial_package_list('Binary', binary)
    print_partial_package_list('Source', source)

    prev_pkg = None
    prev_type = None
    for interface in sorted(list_interfaces(version)):
        if interface.package != prev_pkg:
            click.secho(f'== {interface.package} ==', fg='bright_cyan')
            prev_pkg = interface.package
            prev_type = None
        if interface.type != prev_type:
            click.secho(f'  {interface.type}', fg='cyan')
            prev_type = interface.type
        click.secho(f'    {interface.name}', fg='white')
