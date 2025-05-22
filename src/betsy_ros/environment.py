from .interfaces import ROSInterface
from .workspace import get_ros_version
import re

ACTION_TYPE = re.compile(r'^([\w_]+/\w+)Action(Goal|Result|Feedback)$')


class MasterStrategy:
    def __init__(self, ros_version=None):
        if ros_version is None:
            ros_version, _ = get_ros_version()

        self.ros_version = ros_version

        if self.ros_version == 1:
            import rosgraph
            self.master_strategy = rosgraph.Master('/betsy_ros')
        else:
            from ros2cli.node.strategy import NodeStrategy
            self.master_strategy = NodeStrategy({})

    def __enter__(self):
        if self.ros_version == 2:
            self.master_strategy.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.ros_version == 2:
            self.master_strategy.__exit__(exc_type, exc_value, traceback)

    def get_ros1_actions(self):
        # special implementation since there's no neat API call in ROS 1
        seen_components = set()
        for topic, topic_type in self.master_strategy.getTopicTypes():
            m = ACTION_TYPE.match(topic_type)
            if not m:
                continue
            action_type, component = m.groups()
            if component == 'Feedback':
                # Just deal with Goal/Result
                continue
            if action_type in seen_components:
                action_name, _, _ = topic.rpartition('/')
                yield action_name, action_type
                seen_components.remove(action_type)
            else:
                seen_components.add(action_type)


def _iteration_helper(iterable, interface_type, include_types=False):
    for name, interface_types in iterable:
        if include_types:
            if not isinstance(interface_types, list):
                interface_types = [interface_types]
            interfaces = [ROSInterface.from_string(s, interface_type) for s in interface_types]
            # Most cases, should only be one
            if len(interfaces) == 1:
                yield name, interfaces[0]
            else:
                yield name, interfaces
        else:
            yield name


def get_topics(ros_version=None, include_types=False):
    """Iterate through all the topics currently available."""

    with MasterStrategy(ros_version) as ms:
        if ms.ros_version == 1:
            iterable = ms.master_strategy.getTopicTypes()
        else:
            iterable = ms.master_strategy.get_topic_names_and_types()

        yield from _iteration_helper(iterable, 'msg', include_types)


def get_services(ros_version=None, include_types=False):
    """Iterate through all the service names currently available."""
    with MasterStrategy(ros_version) as ms:
        if ms.ros_version == 1:
            names_and_nodes = ms.master_strategy.getSystemState()[2]
            if include_types:
                from rosservice import get_service_type
                iterable = []
                for name, nodes in names_and_nodes:
                    iterable.append((name, get_service_type(name)))
            else:
                iterable = names_and_nodes
        else:
            iterable = ms.master_strategy.get_service_names_and_types()

        yield from _iteration_helper(iterable, 'srv', include_types)


def get_actions(ros_version=None, include_types=False):
    with MasterStrategy(ros_version) as ms:
        if ms.ros_version == 1:
            iterable = ms.get_ros1_actions()
        else:
            from ros2action.api import get_action_names_and_types
            iterable = get_action_names_and_types(node=ms.master_strategy)

        yield from _iteration_helper(iterable, 'action', include_types)
