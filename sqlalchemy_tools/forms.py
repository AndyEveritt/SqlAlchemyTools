from flask_wtf import FlaskForm as _FlaskForm
from wtforms_alchemy import model_form_factory as _model_form_factory

_BaseModelForm = _model_form_factory(_FlaskForm)


def create_model_form(db):
    class ModelForm(_BaseModelForm):
        @classmethod
        def get_session(cls):
            return db.session

    return ModelForm
