from typing import Optional

from synapse import user
from synapse.user import generate_matrix_id


def post(external_id: str, display_name: str, email: Optional[str] = None):
    # Check if User exists, return matrix ID if it does
    # If user doesn't exist create user and return matrix ID

    matrix_id = user.get_matrix_account_id(external_id)
    if matrix_id is None:
        generated_matrix_id = generate_matrix_id(external_id)
        user.create_or_modify_user(generated_matrix_id, display_name, external_id, email)
        matrix_id = generated_matrix_id
    return matrix_id


def put(matrix_id: str, external_id: str, display_name: str, email: Optional[str] = None):
    user.create_or_modify_user(matrix_id, display_name, external_id, email)
    return matrix_id
