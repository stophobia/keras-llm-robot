import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import Body
from WebUI.Server.chat.completion import completion
from WebUI.Server.utils import (FastAPI, MakeFastAPIOffline, BaseResponse, ListResponse)
from WebUI.configs.serverconfig import OPEN_CROSS_DOMAIN
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from WebUI.Server.chat.chat import chat
from WebUI.Server.embeddings_api import embed_texts_endpoint
from WebUI.Server.chat.openai_chat import openai_chat
from WebUI.Server.llm_api import (list_running_models, get_running_models, list_config_models,
                            change_llm_model, stop_llm_model,
                            get_model_config, list_search_engines)
from WebUI.Server.utils import(get_prompt_template)
from typing import List, Literal
from __about__ import __version__

async def document():
    return RedirectResponse(url="/docs")

def create_app(run_mode: str = None):
    app = FastAPI(
        title="Langchain-Chatchat API Server",
        version=__version__
    )
    MakeFastAPIOffline(app)
    # Add CORS middleware to allow all origins
    # 在config.py中设置OPEN_DOMAIN=True，允许跨域
    # set OPEN_DOMAIN=True in config.py to allow cross-domain
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    mount_app_routes(app, run_mode=run_mode)
    return app

def mount_app_routes(app: FastAPI, run_mode: str = None):
    app.get("/",
            response_model=BaseResponse,
            summary="swagger 文档")(document)

    # Tag: Chat
    app.post("/chat/fastchat",
             tags=["Chat"],
             summary="与llm模型对话(直接与fastchat api对话)",
             )(openai_chat)

    app.post("/chat/chat",
             tags=["Chat"],
             summary="与llm模型对话(通过LLMChain)",
             )(chat)

    #app.post("/chat/search_engine_chat",
    #         tags=["Chat"],
    #         summary="与搜索引擎对话",
    #         )(search_engine_chat)

    #app.post("/chat/feedback",
    #         tags=["Chat"],
    #         summary="返回llm模型对话评分",
    #         )(chat_feedback)

    # 知识库相关接口
    #mount_knowledge_routes(app)

    # LLM模型相关接口
    app.post("/llm_model/list_running_models",
             tags=["LLM Model Management"],
             summary="列出当前已加载的模型",
             )(list_running_models)
    
    app.post("/llm_model/get_running_models",
             tags=["LLM Model Management"],
             summary="列出当前已加载的模型",
             )(get_running_models)

    app.post("/llm_model/list_config_models",
             tags=["LLM Model Management"],
             summary="列出configs已配置的模型",
             )(list_config_models)

    app.post("/llm_model/get_model_config",
             tags=["LLM Model Management"],
             summary="获取模型配置（合并后）",
             )(get_model_config)

    app.post("/llm_model/stop",
             tags=["LLM Model Management"],
             summary="停止指定的LLM模型（Model Worker)",
             )(stop_llm_model)

    app.post("/llm_model/change",
             tags=["LLM Model Management"],
             summary="切换指定的LLM模型（Model Worker)",
             )(change_llm_model)

    # 服务器相关接口
    #app.post("/server/configs",
    #         tags=["Server State"],
    #         summary="获取服务器原始配置信息",
    #         )(get_server_configs)

    #app.post("/server/list_search_engines",
    #         tags=["Server State"],
    #         summary="获取服务器支持的搜索引擎",
    #         )(list_search_engines)

    @app.post("/server/get_prompt_template",
             tags=["Server State"],
             summary="获取服务区配置的 prompt 模板")
    def get_server_prompt_template(
        type: Literal["llm_chat", "knowledge_base_chat", "search_engine_chat", "agent_chat"]=Body("llm_chat", description="模板类型，可选值：llm_chat，knowledge_base_chat，search_engine_chat，agent_chat"),
        name: str = Body("default", description="模板名称"),
    ) -> str:
        return get_prompt_template(type=type, name=name)

    # 其它接口
    app.post("/other/completion",
             tags=["Other"],
             summary="要求llm模型补全(通过LLMChain)",
             )(completion)

    app.post("/other/embed_texts",
            tags=["Other"],
            summary="将文本向量化，支持本地模型和在线模型",
            )(embed_texts_endpoint)