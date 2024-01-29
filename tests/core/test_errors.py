from uuid import uuid4

from core.errors import DoesNotExistError


def test_does_not_exist_error() -> None:
    unknown_id = uuid4()
    json = DoesNotExistError("Unit", "id", str(unknown_id)).get_error_json_response(404)
    assert json.status_code == 404
    assert (
            json.body.decode("utf-8")
            == '{"error":{"message":"Unit with id<'
            + str(unknown_id)
            + '> does not exist."}}'
    )

