from flask_validator import *
from .base import BaseModel
from .database import arrow


class ValidateFK(validator.Validator):
    """ Validate the FK pk value exists """

    def __init__(self, field, fk_model: BaseModel, allow_null=True, throw_exception=False, message=None):
        self.fk_model = fk_model

        validator.Validator.__init__(self, field, allow_null, throw_exception, message)

    def check_value(self, value):
        return True if self.fk_model.get(value) else False


class ValidateDatetime(validator.Validator):
    """ Validate the field is of type `arrow.Arrow` """

    def check_value(self, value):
        return True if type(value) is arrow.Arrow else False
