from config import MATRIX_ADMIN_TOKEN


def get_headers():
    return {"Authorization": f"Bearer {MATRIX_ADMIN_TOKEN}"}
