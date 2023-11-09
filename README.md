![image of Betsy Ross](logo.jpg)

# Betsy ROS
In this time of revolution between the regimes of ROS 1 and ROS 2, Betsy ROS creates a unified banner

Translation: This package is a unified Python API for certain "meta" ROS API calls that work the same in ROS 1 and ROS 2.

## Functionality
### Workspace
 * `get_workspace_root` returns a `BuildType` and `pathlib.Path` indicating the type and location of the current workspace.
   * `BuildType` can be `CATKIN_MAKE`, `CATKIN_TOOLS`, or `COLCON`
 * `get_ros_version` returns an `int` and `str` indicating the ROS version (1 or 2) and the distro short-name (e.g. `lunar`, `bouncy`)

### Packages
 * `get_package_name_from_path` returns the name of the package that the initial path is in (including subfolders)
 * `get_package_names` returns a set of strings of all the current package names, including the binary packages and the workspace packages
 * `find_package` returns the path to a given package
 * `is_binary_ros` returns True if the path passed to it is in the `/opt/ros` folder

### Interfaces
(i.e. messages, services and actions)

 * The class `ROSInterface` has three key attributes:
  * package
  * type
  * name
 * `list_interfaces` yields `ROSInterface` instances for all messages/services/actions in the environment.

## Credit
Package logo from artwork by Jean Leon Gerome Ferris (1863–1930):
[Betsy Ross 1777](https://commons.wikimedia.org/wiki/File:Betsy_Ross_1777_cph.3g09905.jpg)
