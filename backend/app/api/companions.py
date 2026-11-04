import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, VerificationStatus
from app.models.journey import Journey, JourneyStatus
from app.models.companion import CompanionRequest, CompanionGroup, RequestStatus, GroupStatus
from app.schemas.companion import (
    CompanionCandidate, CompanionRequestCreate, CompanionRequestUpdate, CompanionRequestResponse, CompanionGroupResponse
)
from app.services.auth_service import get_current_user, get_current_verified_user
from app.services.matching_service import (
    find_companion_matches, create_companion_request, update_request_status
)

router = APIRouter(prefix="/companions", tags=["Companion Matching"])

@router.get("/matches/{journey_id}", response_model=List[CompanionCandidate])
async def get_matches(
    journey_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")

    matches = await find_companion_matches(db, journey)
    return matches

@router.post("/requests", response_model=CompanionRequestResponse, status_code=status.HTTP_201_CREATED)
def send_request(
    req_in: CompanionRequestCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    try:
        req = create_companion_request(
            db=db,
            sender=current_user,
            receiver_journey_id=req_in.receiver_journey_id,
            initial_message=req_in.initial_message
        )
        return req
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/requests", response_model=List[CompanionRequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(CompanionRequest).filter(
        (CompanionRequest.sender_id == current_user.id) | (CompanionRequest.receiver_id == current_user.id)
    ).order_by(CompanionRequest.created_at.desc()).all()

    # Hydrate names
    res = []
    for r in requests:
        item = CompanionRequestResponse.model_validate(r)
        item.sender_name = r.sender.name if r.sender else "User"
        item.receiver_name = r.receiver.name if r.receiver else "User"
        res.append(item)
    return res

@router.patch("/requests/{request_id}", response_model=CompanionRequestResponse)
def update_status_endpoint(
    request_id: int,
    body: CompanionRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        req = update_request_status(db, request_id, current_user, body.status)
        item = CompanionRequestResponse.model_validate(req)
        item.sender_name = req.sender.name
        item.receiver_name = req.receiver.name
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups/{group_id}", response_model=CompanionGroupResponse)
def get_group_details(
    group_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    group = db.query(CompanionGroup).filter(CompanionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Companion group not found.")

    user_ids = json.loads(group.user_ids_json)
    if current_user.id not in user_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to view this companion group.")

    journey_ids = json.loads(group.journey_ids_json)

    return CompanionGroupResponse(
        id=group.id,
        request_id=group.request_id,
        user_ids=user_ids,
        journey_ids=journey_ids,
        meeting_point_name=group.meeting_point_name,
        meeting_point_lat=group.meeting_point_lat,
        meeting_point_lng=group.meeting_point_lng,
        meeting_time=group.meeting_time,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at
    )

