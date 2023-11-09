import pathlib

from .workspace import get_ros_version
from .packages import get_package_names

INTERFACE_TYPES = ['msg', 'srv', 'action']


class ROSInterface:
    def __init__(self, package, interface_type, name):
        self.package = package
        self.type = interface_type
        self.name = name

    @staticmethod
    def from_string(s, interface_type=None):
        pieces = s.split('/')
        # If only two pieces, assume the interface_type is missing
        # i.e. convert geometry_msgs/Point to geometry_msgs/msg/Point
        if len(pieces) == 2:
            return ROSInterface(pieces[0], interface_type, pieces[1])
        # If three pieces, assume the interface type is specified
        elif len(pieces) == 3:
            return ROSInterface(*pieces)
        else:
            raise RuntimeError(f'Cannot parse interface for "{s}"')

    def to_string(self, two_part=True):
        if two_part:
            return f'{self.package}/{self.name}'
        else:
            return f'{self.package}/{self.type}/{self.name}'

    def __lt__(self, other):
        if self.package != other.package:
            return self.package < other.package

        i0 = INTERFACE_TYPES.index(self.type)
        i1 = INTERFACE_TYPES.index(other.type)
        if i0 != i1:
            return i0 < i1

        return self.name < other.name

    def __repr__(self):
        return self.to_string()


def list_interfaces(ros_version=None, interface_types=None):
    """yields ROSInterface instances for all messages/services/actions in the environment."""
    if ros_version is None:
        ros_version, _ = get_ros_version()
    if interface_types is None:
        interface_types = INTERFACE_TYPES

    if ros_version == 1:
        import rospkg
        from rosmsg import _list_types, _get_package_paths

        rospack = rospkg.RosPack()
        for pkg in get_package_names(ros_version):
            package_paths = _get_package_paths(pkg, rospack)
            for package_path_s in package_paths:
                package_path = pathlib.Path(package_path_s)
                for interface_type in interface_types:
                    interface_path = package_path / interface_type
                    if not interface_path.exists():
                        continue
                    for i_name in _list_types(str(interface_path),
                                              interface_type,
                                              '.' + interface_type):
                        yield ROSInterface(pkg, interface_type, i_name)
    else:
        from rosidl_runtime_py import get_interfaces
        for pkg, pkg_interfaces in get_interfaces().items():
            for pkg_interface in pkg_interfaces:
                interface_type, i_name = pkg_interface.split('/')
                if interface_type not in interface_types:
                    continue
                yield ROSInterface(pkg, interface_type, i_name)
