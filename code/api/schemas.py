from marshmallow import ValidationError, Schema, fields


def validate_string(value):
    if value == '':
        raise ValidationError('Field may not be blank.')


class ObservableSchema(Schema):
    type = fields.String(
        validate=validate_string,
        required=True,
    )
    value = fields.String(
        validate=validate_string,
        required=True,
    )
