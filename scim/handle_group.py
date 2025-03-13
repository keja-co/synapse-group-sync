# Matrix has no concept of groups, we are instead mapping any users within a group to specific rooms in Matrix.
from typing import TYPE_CHECKING, Union

from config import IDP_GROUP_TO_ROOM
from synapse.room import add_to_rooms
from utils import LogLevel, log

if TYPE_CHECKING:
    from scim.main import SCIMGroup, SCIMGroupUpdate


def process(group: Union['SCIMGroup', 'SCIMGroupUpdate']):
    assigned_rooms = IDP_GROUP_TO_ROOM.get(group.externalId, [])

    if group.members is not None:
        for member in group.members:
            # Check member is of type User
            if member.ref == "Group":
                continue

            # Add User to Rooms
            log(LogLevel.DEBUG, f"Attempting to add {member.value} to rooms: {assigned_rooms}")
            matrix_id = member.value
            add_to_rooms(matrix_id, assigned_rooms)

        # TODO: Remove users from rooms if they are no longer in the group
        # Need to fetch all users in each effected room and compare to group members
    log(LogLevel.DEBUG, f"Processed group: {group.displayName} ({group.externalId}), but found no members.")
