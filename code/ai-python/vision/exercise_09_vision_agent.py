"""
AI-Python-09.1 实战 2: Vision Agent — 图文问答系统
结合图片理解 + 知识库搜索，实现图文混合问答
"""

import base64
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Vision LLM 和 Text LLM（可分别配置不同模型）
# 请替换为你的实际 API Key
vision_llm = ChatOpenAI(
    model="glm-4v-flash",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key="your-api-key-here",
    temperature=0.3
)

text_llm = ChatOpenAI(
    model="gpt-4o-mini",  # 或其他文本模型
    api_key="your-api-key-here",
    temperature=0.5
)


# ========== Tool 1: 图片分析 ==========
@tool
def analyze_image(image_path: str, question: str) -> str:
    """
    分析图片内容并回答问题。

    Args:
        image_path: 图片文件路径（本地）
        question: 关于图片的问题

    Returns:
        图片分析结果
    """
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": f"请仔细观察这张图片，回答以下问题：\n{question}"},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
        ]
    )

    response = vision_llm.invoke([message])
    return response.content


# ========== Tool 2: 知识库搜索（模拟） ==========
@tool
def search_wiki(query: str) -> str:
    """
    搜索维基百科获取背景知识（模拟实现）。

    Args:
        query: 搜索关键词

    Returns:
        相关知识摘要
    """
    # 实际项目中可接入真实搜索 API 或向量库
    mock_knowledge = {
        "react": "React 是一个用于构建用户界面的 JavaScript 库，由 Facebook 维护。",
        "microservices": "微服务架构是一种将单一应用程序开发为一套小型服务的方法。",
        "kubernetes": "Kubernetes (K8s) 是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。",
        "redis": "Redis 是一个开源的内存数据结构存储，可用作数据库、缓存和消息代理。"
    }

    # 简单模糊匹配
    for key, value in mock_knowledge.items():
        if key.lower() in query.lower():
            return f"[来自维基百科] {value}"

    return f"[来自维基百科] 未找到关于 '{query}' 的直接信息，建议提供更具体的关键词。"


# ========== Vision Agent ==========
def create_vision_agent():
    """创建图文混合 Agent"""

    # 定义工具列表
    tools = [analyze_image, search_wiki]

    # 获取 ReAct 模板
    prompt = hub.pull("hwchase17/react")

    # 创建 Agent
    agent = create_react_agent(
        llm=text_llm,
        tools=tools,
        prompt=prompt
    )

    # 创建 AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent_executor


# ========== 问答场景 ==========
def ask_vision_question(image_path: str, question: str):
    """
    提问 Vision Agent

    Args:
        image_path: 图片路径
        question: 用户问题
    """
    executor = create_vision_agent()

    # 构建输入，将图片路径注入
    input_data = {
        "input": f"""
        用户上传了一张图片：{image_path}
        用户的问题是：{question}

        请先使用 analyze_image 工具分析图片内容，
        然后根据需要使用 search_wiki 工具补充背景知识，
        最后给出完整、准确的回答。
        """
    }

    try:
        result = executor.invoke(input_data)
        return result["output"]
    except Exception as e:
        return f"执行出错：{str(e)}"


# ========== 示例场景 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("Vision Agent 图文问答系统")
    print("=" * 60)

    # 场景 1：代码截图 + 技术问答
    print("\n【场景 1】代码架构理解 + 技术背景补充")
    print("-" * 60)

    architecture_img = "microservices_arch.png"  # 替换为实际图片
    question_1 = "这张架构图用了哪些技术栈？Kubernetes 是用来做什么的？"

    print(f"问题：{question_1}")
    print(f"图片：{architecture_img}")

    try:
        answer = ask_vision_question(architecture_img, question_1)
        print(f"\n回答：\n{answer}\n")
    except FileNotFoundError:
        print(f"[提示] 请准备图片 {architecture_img}\n")

    # 场景 2：产品截图 + 功能分析
    print("\n【场景 2】产品界面分析")
    print("-" * 60)

    product_img = "app_screenshot.jpg"  # 替换为实际图片
    question_2 = "这个 App 的主要功能是什么？用户体验有哪些可改进之处？"

    print(f"问题：{question_2}")
    print(f"图片：{product_img}")

    try:
        answer = ask_vision_question(product_img, question_2)
        print(f"\n回答：\n{answer}\n")
    except FileNotFoundError:
        print(f"[提示] 请准备图片 {product_img}\n")

    # 场景 3：文档截图 + 知识检索
    print("\n【场景 3】技术文档理解 + 最佳实践")
    print("-" * 60)

    doc_img = "api_doc.png"  # 替换为实际图片
    question_3 = "这个 API 文档描述的是什么功能？使用时需要注意什么？"

    print(f"问题：{question_3}")
    print(f"图片：{doc_img}")

    try:
        answer = ask_vision_question(doc_img, question_3)
        print(f"\n回答：\n{answer}\n")
    except FileNotFoundError:
        print(f"[提示] 请准备图片 {doc_img}\n")

    print("=" * 60)
    print("💡 提示：")
    print("1. Vision Agent 会自动判断是否需要搜索知识库")
    print("2. 图片路径需要是本地绝对路径或相对路径")
    print("3. 复杂问题可能需要多次工具调用，耐心等待")
    print("=" * 60)
