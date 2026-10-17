from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mysite.chain.ai import chain, check_question

router = APIRouter(prefix="/chat", tags=["AI Chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    status: str
    answer: str


@router.post("/ask", response_model=ChatResponse)
async def ask_chat_ai(request: ChatRequest):
    data = {"question": request.question}


    checked_data = check_question(data)
    if not checked_data["allowed"]:
        raise HTTPException(
            status_code=400,
            detail="Суроо тыюу салынган же кооптуу сөздөрдү камтыйт."
        )

    try:
        answer = chain.invoke(data)

        return {
            "status": "success",
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI жообун иштетүүдө ката кетти: {str(e)}"
        )