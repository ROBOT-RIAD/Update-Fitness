# # chatbot/service.py
# import os
# import uuid
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# from langchain_core.messages import SystemMessage
# from langgraph.graph import StateGraph, MessagesState, START
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# from django.conf import settings

# load_dotenv()


# DB_URI = os.getenv("DB_URI") or getattr(settings, "DB_URI", None)
# if not DB_URI:
#     raise ValueError("❌ DB_URI not found in environment or settings.")

# api_key = settings.OPENAI_API_KEY
# model = init_chat_model(model="gpt-3.5-turbo", api_key=api_key)


# async def chat(thread_id: str, user_message: str):
#     async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:  
#         await checkpointer.setup()

#         async def call_model(state: MessagesState):
#             system_msg = SystemMessage("You are a fitness expert specializing in creating personalized workout and meal plans. Provide suggestions based on user preferences, fitness levels, and goals. Don't include any out of the context information. Be concise and to the point.")
#             response = await model.ainvoke([system_msg] + state["messages"])
#             return {"messages": response}

#         builder = StateGraph(MessagesState)
#         builder.add_node(call_model)
#         builder.add_edge(START, "call_model")

#         graph = builder.compile(checkpointer=checkpointer)  

#         config = {
#             "configurable": {
#                 "thread_id": thread_id
#             }
#         }
        
#         messages = []
#         async for chunk in graph.astream(
#             {"messages": [{"role": "user", "content": user_message}]},
#             config,  
#             stream_mode="values"
#         ):
#             messages = chunk["messages"]
        
#         return messages[-1] if messages else None
