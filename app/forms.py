from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired


class BaseForm(FlaskForm):
    cub_name = StringField("Cub Name", validators=[DataRequired()])
    date = HiddenField(
        "date",
        validators=[
            DataRequired(
                message=" ".join(
                    (
                        "Date field must be attached to form."
                        "This is a hidden field and the presence of",
                        "this message indicates an error in they system."
                        "Please contact the developer.",
                    )
                )
            )
        ],
    )
    time = HiddenField(
        "time",
        validators=[
            DataRequired(
                message=" ".join(
                    (
                        "Time field must be attached to form."
                        "This is a hidden field and the presence of",
                        "this message indicates an error in they system."
                        "Please contact the developer.",
                    )
                )
            )
        ],
    )
    parent_signature = HiddenField(
        "parent signature",
        validators=[
            DataRequired(
                message=" ".join(
                    (
                        "Parent signature must be attached to form.",
                        "This is a hidden field and the precense of",
                        "this message indicates an error in the system.",
                        "Please contact the developer",
                    )
                )
            )
        ],
    )


class SignInForm(BaseForm):
    cub_signature = HiddenField(
        "cub signature",
        validators=[
            DataRequired(
                message=" ".join(
                    (
                        "Parent signature must be attached to form.",
                        "This is a hidden field and the precense of",
                        "this message indicates an error in the system.",
                        "Please contact the developer",
                    )
                )
            )
        ],
    )


class SignOutForm(BaseForm):
    pass
