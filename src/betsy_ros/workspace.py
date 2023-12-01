import os
import pathlib
from enum import Enum


class BuildType(Enum):
    CATKIN_MAKE = 1
    CATKIN_TOOLS = 2
    COLCON = 3


def _get_parent_dirs(cur_dir):
    """Iterate over all parent directories (including the starting directory)."""
    folder = cur_dir.resolve()
    while folder:
        yield folder
        if folder.parent == folder:
            return
        else:
            folder = folder.parent


def get_workspace_root(cur_dir=pathlib.Path('.')):
    """
    Return the workspace root and the type of workspace.

    If no build tool has been run yet, return the highest directory with a src subfolder
    If catkin_make or catkin build has been run, return the directory with the proper metadata.
    If colcon, there's no metadata, so we return the highest directory with a src subfolder AND a build subfolder.
    """
    prefix_path = os.environ.get('COLCON_PREFIX_PATH')
    if prefix_path:
        first = prefix_path.split(':')[0]
        install_dir = pathlib.Path(first)
        return BuildType.COLCON, install_dir.parent
    highest_candidate = None
    for folder in _get_parent_dirs(cur_dir):
        if (folder / '.catkin_workspace').exists():
            return BuildType.CATKIN_MAKE, folder
        elif (folder / '.catkin_tools').exists():
            return BuildType.CATKIN_TOOLS, folder
        elif (folder / 'src').exists():
            if (folder / 'build').exists():
                # If we're here, it is not CATKIN
                return BuildType.COLCON, folder
            highest_candidate = folder

    return None, highest_candidate


def get_ros_version(fail_quietly=False):
    """Return ROS Version and Distro."""
    env = os.environ
    version = env.get('ROS_VERSION')
    distro = env.get('ROS_DISTRO')
    if version and distro:
        return int(version), distro

    if fail_quietly:
        return version, distro

    raise RuntimeError('Unable to determine ROS distro. Please source workspace.')
