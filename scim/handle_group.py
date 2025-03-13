# Matrix has no concept of groups, we are instead mapping any users within a group to specific rooms in Matrix.
from typing import TYPE_CHECKING, Union

from config import IDP_GROUP_TO_ROOM
from synapse.room import add_to_rooms

if TYPE_CHECKING:
    from scim.main import SCIMGroup, SCIMGroupUpdate


def process(group: Union['SCIMGroup', 'SCIMGroupUpdate']):
    assigned_rooms = IDP_GROUP_TO_ROOM.get(group.externalId, [])

    for member in group.members:
        # Check member is of type User
        if member.ref == "Group":
            continue

        # Add User to Rooms
        matrix_id = member.value
        add_to_rooms(matrix_id, assigned_rooms)

    # TODO: Remove users from rooms if they are no longer in the group
    # Need to fetch all users in each effected room and compare to group members
