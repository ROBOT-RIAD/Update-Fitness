from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ChatBotMessage
from .service import chat

from asgiref.sync import async_to_sync

import asyncio
import threading
from queue import Queue, Empty

def stream_chat_sync(user_id, message):
    """
    Safely bridge async generator → sync generator
    using a dedicated event loop thread.
    """
    q = Queue()
    SENTINEL = object()

    async def runner():
        try:
            async for chunk in chat(user_id, message):
                q.put(chunk)
        finally:
            q.put(SENTINEL)

    def start_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner())
        loop.close()

    threading.Thread(target=start_loop, daemon=True).start()

    while True:
        item = q.get()
        if item is SENTINEL:
            break
        yield item




class FitnessChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Chat with AI Fitness Assistant",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["message"],
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        tags=["AI Fitness Chat"]
    )
    def post(self, request):
        user = request.user
        user_message = request.data.get("message")

        if not user_message:
            return Response({"error": "Message is required."}, status=400)

        full_response = []
       
        return Response("od")
        # def event_stream():
        #     for chunk in stream_chat_sync(str(user.id), user_message):
        #         full_response.append(chunk)
        #         yield chunk.encode("utf-8")

        #     ChatBotMessage.objects.create(
        #         user=user,
        #         user_input=user_message,
        #         ai_response={"text": "".join(full_response)}
        #     )

        # return StreamingHttpResponse(
        #     event_stream(),
        #     content_type="text/event-stream",
        #     headers={
        #         "Cache-Control": "no-cache",
        #         "X-Accel-Buffering": "no",
        #     }
        # )

