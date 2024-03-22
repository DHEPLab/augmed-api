import pytest
from src.user.utils.pcrypt import generate_salt, pcrypt, verify


@pytest.fixture
def test_password():
    return "9eNLBWpws6TCGk8_ibQn"


@pytest.fixture
def salt():
    return generate_salt()

@pytest.fixture
def digt(test_password, salt):
    return pcrypt(test_password, salt)


def test_generate_salt(salt):
    assert salt is not None
    assert isinstance(salt, str)
    assert len(salt) == 24


def test_pcrypt(test_password, salt):
    salt = generate_salt()

    derived_key = pcrypt(test_password, salt)

    assert derived_key is not None
    assert isinstance(derived_key, str)
    assert len(derived_key) == 172

    
def test_verify(test_password, salt, digt):
    un_match_password = "?FAdWqd6pPuPX.mc"
    un_match_salt = generate_salt()

    assert verify(test_password, salt, digt) == True

    assert verify(un_match_password, salt, digt) == False
    assert verify(test_password, un_match_salt, digt) == False
