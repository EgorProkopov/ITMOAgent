from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.model import ChatModel
from app.containers import AppContainer
from app.api.utils import QuestionRequest, AnswerResponse


router = APIRouter()


@router.post("/api/request", response_model=AnswerResponse)
@inject
async def request_answer(
    request: QuestionRequest,
    chat_model: ChatModel = Depends(Provide[AppContainer.chat_model])
):
    json_response = chat_model.get_answer(request.query)
    json_response['id'] = request.id
    return json_response