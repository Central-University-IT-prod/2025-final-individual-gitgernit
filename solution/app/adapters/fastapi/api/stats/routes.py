import fastapi
from dishka.integrations.fastapi import DishkaRoute

import app.adapters.fastapi.api.stats.advertisers.routes
import app.adapters.fastapi.api.stats.campaigns.routes

stats_router = fastapi.APIRouter(route_class=DishkaRoute)

stats_router.include_router(
    app.adapters.fastapi.api.stats.campaigns.routes.campaigns_router,
    prefix='/campaigns',
)
stats_router.include_router(
    app.adapters.fastapi.api.stats.advertisers.routes.advertisers_router,
    prefix='/advertisers',
)
