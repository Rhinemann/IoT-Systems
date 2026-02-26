from marshmallow import Schema, fields

from agent.src.schema.gps_schema import GpsSchema


class ParkingSchema(Schema):
    gps = fields.Nested(GpsSchema)
    empty_count = fields.Int()
