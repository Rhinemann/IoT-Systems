from marshmallow import Schema, fields


class AccelerometerSchema(Schema):
    x = fields.Float()
    y = fields.Float()
    z = fields.Float()
