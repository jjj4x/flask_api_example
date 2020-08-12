from myapp import (
    APIMethodView,
    APIBlueprint,
    GuysRequestSchema,
    GuysResponseSchema,
    jwt_required,
    parse,
)


GUYS_BLUEPRINT = APIBlueprint('guys', __name__)


class GuysView(APIMethodView):
    schema = GuysResponseSchema()

    @jwt_required()
    @parse(GuysRequestSchema(), location='query')
    def get(self, _, r):
        """
        Guys detail view and some other info.

        ---
        description: Get a gist
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
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

        if r['full_name'] == '1':
            return {'hey'}
        if r['full_name'] == '2':
            raise RuntimeError('Fail')
        if r['full_name'] == '3':
            return self.schema, {'data': {'identity': r['full_name']}}
