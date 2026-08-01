from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.mongodb import users_collection, chat_collection
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── request body for role change ──
class RoleUpdate(BaseModel):
    role: str   # "user" or "admin"


# ── List all users ─────────────────────────────────────────────
@router.get("/users")
async def list_users(current_user: dict = Depends(require_admin)):
    users = await users_collection.find(
        {},
        {"_id": 0, "hashed_password": 0}   # never expose password hash
    ).to_list(length=100)

    return {
        "total": len(users),
        "users": users,
        "requested_by": current_user["username"]
    }


# ── Get single user ────────────────────────────────────────────
@router.get("/users/{username}")
async def get_user(
    username: str,
    current_user: dict = Depends(require_admin)
):
    user = await users_collection.find_one(
        {"username": username},
        {"_id": 0, "hashed_password": 0}
    )
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    return user


# ── Delete a user ──────────────────────────────────────────────
@router.delete("/users/{username}")
async def delete_user(
    username: str,
    current_user: dict = Depends(require_admin)
):
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    result = await users_collection.delete_one({"username": username})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    # also delete their chat history from MongoDB
    await chat_collection.delete_many({"user_id": username})

    return {
        "message": f"User '{username}' deleted successfully",
        "deleted_by": current_user["username"]
    }


# ── Change user role ───────────────────────────────────────────
@router.patch("/users/{username}/role")
async def change_role(
    username: str,
    body: RoleUpdate,
    current_user: dict = Depends(require_admin)
):
    if body.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")

    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    result = await users_collection.update_one(
        {"username": username},
        {"$set": {"role": body.role}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    return {
        "message": f"Role of '{username}' changed to '{body.role}'",
        "updated_by": current_user["username"]
    }


# ── View any user's persistent chat history ────────────────────
@router.get("/users/{username}/history")
async def get_user_history(
    username: str,
    current_user: dict = Depends(require_admin)
):
    sessions = await chat_collection.find(
        {"user_id": username},
        {"_id": 0}
    ).to_list(length=100)

    return {
        "username": username,
        "total_sessions": len(sessions),
        "sessions": sessions,
        "requested_by": current_user["username"]
    }


# ── Delete all of a user's chat history ───────────────────────
@router.delete("/users/{username}/history")
async def clear_user_history(
    username: str,
    current_user: dict = Depends(require_admin)
):
    result = await chat_collection.delete_many({"user_id": username})

    return {
        "message": f"Deleted {result.deleted_count} session(s) for '{username}'",
        "deleted_by": current_user["username"]
    }