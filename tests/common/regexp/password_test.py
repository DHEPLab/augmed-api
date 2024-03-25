# import pytest
from src.common.regexp.password import validate_password


def test_validate_password_input_valid_return_True():
    valid_password = "9eNLBWpws6TCGk8_ibQn"

    assert validate_password(valid_password) == True  


def test_validate_password_input_no_lower_case_letter_return_True():
    pwd_no_lower_case = "O2XFACVPUM*R=@SE"
 
    assert validate_password(pwd_no_lower_case) == True  


def test_validate_password_input_no_upper_case_letter_return_True():
    pwd_no_upper_case = "o2xfacvpum*r=@se"
 
    assert validate_password(pwd_no_upper_case) == True  


def test_validate_password_input_no_digital_return_False():
    pwd_no_digit = "jcdrBzQWimPfT"
 
    assert validate_password(pwd_no_digit) == False


def test_validate_password_input_no_special_charater_return_False():
    pwd_no_special_character = "ENXPjcEgaqboydr9Ryui"
 
    assert validate_password(pwd_no_special_character) == False


def test_validate_password_input_lens_less_than_8_or_grater_than_128_return_False():
    pwd_len_less_than_8 = "M2@Qi7"
    pwd_len_equal_8 = "M2@Qi7_8"
    pwd_len_equal_128 = "M2@Qi7_8" * 16
    pwd_len_grater_than_128 = pwd_len_equal_128 + 'a'

    assert validate_password(pwd_len_less_than_8) == False
    assert validate_password(pwd_len_grater_than_128) == False

    assert validate_password(pwd_len_equal_8) == True
    assert validate_password(pwd_len_equal_128) == True

