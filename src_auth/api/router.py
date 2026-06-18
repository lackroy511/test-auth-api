from fastapi import APIRouter

from src_auth.features.auth.v1.api import router as auth_v1_router
from src_auth.features.roles.v1.api import router as roles_v1_router
from src_auth.features.users.v1.api import router as users_v1_router

router = APIRouter(prefix="/api/auth")
router.include_router(auth_v1_router)
router.include_router(users_v1_router)
router.include_router(roles_v1_router)
