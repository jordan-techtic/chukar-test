"""Aggregate API v1 routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    activities,
    calendar,
    health,
    historical_management,
    marketing_team_member,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    marketing_team_member.router,
    prefix="/marketing-team-member",
    tags=["marketing-team-member"],
)
api_router.include_router(
    activities.router,
    prefix="/marketing-team-member",
)
api_router.include_router(
    calendar.router,
    prefix="/marketing-team-member",
)
api_router.include_router(
    historical_management.router,
    prefix="/marketing-team-member",
)
