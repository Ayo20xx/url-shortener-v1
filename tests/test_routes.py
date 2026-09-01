from inspect import signature

from app.main import list_url, update


def test_list_route_exposes_limit_and_skip_params():
    params = signature(list_url).parameters
    assert params["skip"].default == 0
    assert params["limit"].default == 10


def test_update_route_requires_payload_and_id():
    params = signature(update).parameters
    assert "id" in params
    assert "input" in params
