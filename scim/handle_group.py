# Matrix has no concept of groups, we are instead mapping any users within a group to specific rooms in Matrix.
from scim.main import SCIMGroup


def process(group: SCIMGroup):
    for user in group.users:
        # Add User to Rooms
        pass

    # TODO: Remove users from rooms if they are no longer in the group