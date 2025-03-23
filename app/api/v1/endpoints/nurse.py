from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Dict, Optional

from ....db.session import get_db
from ....schemas.nurse import *
from ....crud import crud_nurse
from ....utils.passwd_helpers import get_password_hash, verify_password

router = APIRouter()

# Update to use NurseResponse instead of Nurse for list endpoint
@router.get("/", response_model=List[NurseResponse])
async def get_nurses(db: AsyncSession = Depends(get_db)) -> List[Nurse]:
    return await crud_nurse.get_nurses(db)

# Update to use NurseResponse in Union response
@router.get("/{nurse_id}", response_model=Union[NurseResponse, Dict[str, str]])
async def read_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)) -> Union[Nurse, Dict[str, str]]:
    db_nurse = await crud_nurse.get_nurse(db, nurse_id)
    if db_nurse:
        return db_nurse
    return {"detail": "Nurse not found"}

# Update to use NurseResponse in Union response
@router.put("/{nurse_id}", response_model=Union[NurseResponse, Dict[str, str]])
async def update_nurse(nurse_id: int, nurse: NurseUpdate, db: AsyncSession = Depends(get_db)) -> Union[Nurse, Dict[str, str]]:
    db_nurse = await crud_nurse.update_nurse(db, nurse_id, nurse)
    if db_nurse:
        return db_nurse
    return {"detail": "Nurse not found or update failed"}

# Leave delete as is - it returns a boolean or dict
@router.delete("/{nurse_id}", response_model=Union[bool, Dict[str, str]])
async def delete_nurse(nurse_id: int, db: AsyncSession = Depends(get_db)) -> Union[bool, Dict[str, str]]:
    success = await crud_nurse.delete_nurse(db, nurse_id)
    if success:
        return success
    return {"detail": "Nurse not found or delete operation failed"}  

# Use NurseResponse for register endpoint
@router.post("/register", response_model=NurseResponse)
async def register_nurse(nurse: NurseRegister, db: AsyncSession = Depends(get_db)) -> Nurse:
    if await crud_nurse.is_email_taken(db, nurse.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    try:
        # Hash the password using the security module
        nurse.password = get_password_hash(nurse.password)
        created_nurse = await crud_nurse.create_nurse(db, nurse)
        
        if not created_nurse:
            raise HTTPException(
                status_code=500,
                detail="Failed to create nurse"
            )
            
        return created_nurse
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

# Leave login as is - it returns a dict
@router.post("/login", response_model=Dict[str, Union[str, int]])
async def login_nurse(nurse: NurseLogin, db: AsyncSession = Depends(get_db)) -> Dict[str, Union[str, int]]:
    db_nurse = await crud_nurse.get_nurse_by_email(db, nurse.email)
    if not db_nurse:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(nurse.password, db_nurse.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {"message": "Login successful", "nurse_id": db_nurse.id}
