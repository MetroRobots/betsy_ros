import pathlib
import re

from .workspace import get_ros_version, get_workspace_root, _get_parent_dirs

PACKAGE_NAME = re.compile(r'<name>(.*)</name>')


def get_package_name(folder):
    """If this folder is the root of a package, return the name of the package."""
    filename = folder / 'package.xml'
    if filename.exists():
        s = open(filename).read()
        m = PACKAGE_NAME.search(s)
        if m:
            return m.group(1)
        else:
            return folder.stem


def get_package_name_from_path(initial_path=pathlib.Path('.')):
    """Return the name of the package that the initial path is in (including subfolders)."""
    for folder in _get_parent_dirs(initial_path):
        pkg_name = get_package_name(folder)
        if pkg_name:
            return pkg_name


def get_package_names(ros_version=None):
    """returns a set of strings of all the current package names

    including the binary packages and the workspace packages"""
    if ros_version is None:
        ros_version, _ = get_ros_version()

    if ros_version == 1:
        import rospkg
        rospack = rospkg.RosPack()
        return set(rospack.list())
    else:
        from ament_index_python import get_packages_with_prefixes
        return set(get_packages_with_prefixes().keys())


class _FakeNamespace:
    """Used to fake argparser values"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, [])


def is_binary_ros(path):
    return str(path).startswith('/opt/ros/')


_CACHED_DESCRIPTORS = {}


def find_package(package_name, ros_version=None, workspace_root=None):
    if ros_version is None:
        ros_version, _ = get_ros_version()

    if ros_version == 1:
        import rospkg
        rospack = rospkg.RosPack()
        return pathlib.Path(rospack.get_path(package_name))
    else:
        from ros2pkg.api import get_prefix_path
        prefix = get_prefix_path(package_name)

        if prefix and is_binary_ros(prefix):
            return pathlib.Path(f'{prefix}/share/{package_name}')
        else:
            from colcon_core.package_selection import get_package_descriptors

            if workspace_root is None:
                _, workspace_root = get_workspace_root()

            if workspace_root not in _CACHED_DESCRIPTORS:
                args = _FakeNamespace(base_paths=[str(workspace_root)], ignore_user_meta=True)
                descriptors = get_package_descriptors(args)
                _CACHED_DESCRIPTORS[workspace_root] = descriptors
            else:
                descriptors = _CACHED_DESCRIPTORS[workspace_root]

            for descriptor in descriptors:
                if descriptor.name == package_name and descriptor.path:
                    return pathlib.Path(descriptor.path)

            # Install-only path
            return prefix
