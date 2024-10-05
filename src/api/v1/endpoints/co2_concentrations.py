from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def get_cursos(): 
    return {"Map": "Co2 concentration"}
