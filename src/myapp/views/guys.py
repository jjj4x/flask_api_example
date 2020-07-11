from myapp import (
    APIMethodView,
    APIBlueprint,
    GuysRequestSchema,
    GuysResponseSchema,
    parse,
)


GUYS_BLUEPRINT = APIBlueprint('guys', __name__)


class GuysView(APIMethodView):
    schema = GuysResponseSchema()

    # @parse(GuysRequestSchema())
    def get(self, inp):
        """
        Guys detail view.

        ---
        description: Get a gist
        parameters:
            -
                in: query
                schema: GuysRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: GuysResponseSchema
        """

        if inp['full_name'] == '1':
            return {'hey'}
        if inp['full_name'] == '2':
            raise RuntimeError('Fail')
        if inp['full_name'] == '3':
            return self.schema, {'data': {'identity': inp['full_name']}}
