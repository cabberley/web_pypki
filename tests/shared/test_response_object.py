import pytest
from pypki.shared.response_objects import ResponseSuccess, ResponseFailure
from pypki.shared.request_objects import ValidRequestObject, InvalidRequestObject

@pytest.fixture
def response_value():
    return 'Operation performed succesfully'


@pytest.fixture
def response_type():
    return 'ResponseError'


@pytest.fixture
def response_message():
    return 'This is a response error'


def test_response_success_is_true(response_value):
    assert bool(ResponseSuccess(response_value)) is True


def test_response_failure_is_false(response_type, response_message):
    assert bool(ResponseFailure(response_type, response_message)) is False


def test_response_success_contains_value(response_value):
    response = ResponseSuccess(response_value)

    assert response.value == response_value


def test_response_failure_has_type_and_message(response_type, response_message):
    response = ResponseFailure(response_type, response_message)

    assert response.type == response_type
    assert response.message == response_message


def test_response_failure_contains_value(response_type, response_message):
    response = ResponseFailure(response_type, response_message)

    assert response.value == {'type': response_type, 'message': response_message}


def test_response_failure_initialization_with_exception():
    response = ResponseFailure(response_type, Exception('Just an error message'))

    assert bool(response) is False
    assert response.type == response_type
    assert response.message == "Exception: Just an error message"


def test_response_failure_from_invalid_request_object():
    response = ResponseFailure.build_from_invalid_request_object(InvalidRequestObject())

    assert bool(response) is False


def test_response_failure_from_invalid_request_object_with_errors():
    request_object = InvalidRequestObject()
    request_object.add_error('path', 'Is mandatory')
    request_object.add_error('path', "can't be blank")

    response = ResponseFailure.build_from_invalid_request_object(request_object)

    assert bool(response) is False
    assert response.type == ResponseFailure.PARAMETERS_ERROR
    assert response.message == "path: Is mandatory\npath: can't be blank"
