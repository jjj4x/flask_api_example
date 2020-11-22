"""Stats controllers."""
from myapp import APIMethodView, APIBlueprint

STATS_BLUEPRINT = APIBlueprint('stats', __name__)


class StatsView(APIMethodView):
    """Stats resource."""

    def get(self):
        """
        Stats detail view.

        ---
        description: Provides some stats.
        parameters:
            -
                in: query
                schema: StatsRequestSchema
        responses:
            200:
                description: Such response, much info.
                content:
                    application/json:
                        schema: StatsResponseSchema
        """
        return {'hey': self.__class__}
