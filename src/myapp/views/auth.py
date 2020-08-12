from myapp import (
    APIMethodView,
    APIBlueprint,
    APIError,
    JWT,
    AuthRequestSchema,
    AuthResponseSchema,
    parse,
)

AUTH_BLUEPRINT = APIBlueprint('auth', __name__)


class AuthView(APIMethodView):
    schema = AuthResponseSchema()

    @parse(AuthRequestSchema(), location='json', error_status_code=401)
    def post(self, _, r):
        """
        JWT Authentication Endpoint.

        ---
        description: >
            # JWT Authentication Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: AuthRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: AuthResponseSchema
        """

        # FIXME: real handler
        identity = {'id': r['username']}

        if not identity:
            raise APIError(
                'Bad Request: invalid credentials',
                metadata={'status': 401},
                http_status=401,
            )

        return self.schema, {'data': {'access_token': JWT.encode(identity)}}
