from fastapi import APIRouter

from egame179_backend.app.api.echo.schema import Message

router = APIRouter()


@router.post("/", response_model=Message)
async def send_echo_message(incoming_message: Message) -> Message:
    """
    Send echo back to user.

    Args:
        incoming_message (Message): incoming message.

    Returns:
        Message: message same as the incoming.
    """
    return incoming_message
