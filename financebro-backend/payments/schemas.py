from ninja import Schema

class CreateStripeCheckoutSessionSchema(Schema):
    price_id: str
