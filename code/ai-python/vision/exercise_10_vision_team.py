"""
AI-Python-09.1 实战 3: 多模态研究团队
Supervisor 模式协调 Vision Agent + Researcher + Writer
"""

import base64
from typing import Literal, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# ========== 模型配置 ==========
# 请替换为你的实际 API Key
vision_llm = ChatOpenAI(
    model="glm-4v-flash",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key="your-api-key-here",
    temperature=0.3
)

text_llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key="your-api-key-here",
    temperature=0.5
)


# ========== 辅助函数 ==========
def encode_image(image_path: str) -> str:
    """编码图片为 base64"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_with_vision(image_path: str, prompt: str) -> str:
    """用 Vision LLM 分析图片"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    base64_image = encode_image(image_path)

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
        ]
    )

    response = vision_llm.invoke([message])
    return response.content


# ========== Agent 1: Vision Specialist ==========
def create_vision_agent():
    """创建视觉分析专家 Agent"""

    @tool
    def analyze_diagram(image_path: str) -> str:
        """分析架构图或流程图"""
        prompt = """
        请详细分析这张图表：
        1. 识别所有组件/节点
        2. 描述组件之间的关系和连接
        3. 分析数据/控制流向
        4. 指出潜在的设计问题或优化点
        """
        return analyze_with_vision(image_path, prompt)

    @tool
    def extract_text(image_path: str) -> str:
        """提取图片中的文字内容（OCR）"""
        prompt = """
        请提取这张图片中的所有文字：
        1. 完整还原所有可见文本
        2. 保持原有结构和层级
        3. 标注重要信息的类型（如标题、标签、注释）
        """
        return analyze_with_vision(image_path, prompt)

    return create_react_agent(
        model=text_llm,
        tools=[analyze_diagram, extract_text],
        prompt=(
            "你是视觉分析专家。"
            "擅长从图片中提取结构化信息和文字内容。"
            "使用 analyze_diagram 分析图表，使用 extract_text 提取文字。"
        ),
        name="vision_specialist"
    )


# ========== Agent 2: Researcher ==========
def create_researcher_agent():
    """创建研究员 Agent（负责知识检索和背景分析）"""

    @tool
    def search_best_practice(topic: str) -> str:
        """搜索最佳实践（模拟）"""
        knowledge = {
            "microservices": "微服务最佳实践：1) API 网关统一入口 2) 服务注册发现 3) 熔断降级 4) 分布式追踪",
            "database": "数据库设计原则：1) 范式化减少冗余 2) 适当反范式提升性能 3) 索引策略 4) 读写分离",
            "frontend": "前端性能优化：1) 代码分割 2) 懒加载 3) 缓存策略 4) CDN 加速"
        }
        for key, value in knowledge.items():
            if key.lower() in topic.lower():
                return f"[最佳实践] {value}"
        return f"[最佳实践] 未找到关于 '{topic}' 的直接信息"

    return create_react_agent(
        model=text_llm,
        tools=[search_best_practice],
        prompt=(
            "你是研究员。"
            "负责搜索技术背景知识和最佳实践。"
            "使用 search_best_practice 工具查找相关信息。"
        ),
        name="researcher"
    )


# ========== Agent 3: Writer ==========
def create_writer_agent():
    """创建撰稿人 Agent（负责总结和输出）"""

    return create_react_agent(
        model=text_llm,
        tools=[],
        prompt=(
            "你是技术撰稿人。"
            "负责整合团队成员的分析结果，输出结构清晰的技术文档。"
            "确保逻辑连贯、重点突出。"
        ),
        name="writer"
    )


# ========== Supervisor 协调者 ==========
def create_supervisor():
    """创建 Supervisor 路由逻辑"""

    system_prompt = """
    你是多模态研究团队的协调者。

    团队成员：
    - VISION: 负责分析图片内容（架构图、流程图、OCR）
    - RESEARCHER: 负责搜索技术背景和最佳实践
    - WRITER: 负责整合输出

    工作流程：
    1. 收到用户任务后，首先调用 VISION 分析图片
    2. 根据图片内容，调用 RESEARCHER 补充背景知识
    3. 最后调用 WRITER 整合输出

    输出格式：只输出成员名称（VISION、RESEARCHER、WRITER），
    如果任务完成，输出 "FINISH"。
    """

    return ChatOpenAI(
        model="gpt-4o",
        api_key="your-api-key-here",
        temperature=0
    ).bind_tools([
        {"type": "function", "function": {"name": "VISION", "description": "调用视觉分析专家"}},
        {"type": "function", "function": {"name": "RESEARCHER", "description": "调用研究员"}},
        {"type": "function", "function": {"name": "WRITER", "description": "调用撰稿人"}},
        {"type": "function", "function": {"name": "FINISH", "description": "任务完成"}}
    ])


# ========== 主工作流 ==========
def run_vision_team_analysis(image_path: str, task: str):
    """
    运行多模态团队分析

    Args:
        image_path: 图片路径
        task: 用户任务描述

    Returns:
        团队分析结果
    """

    # 创建团队成员
    vision_agent = create_vision_agent()
    researcher_agent = create_researcher_agent()
    writer_agent = create_writer_agent()

    # 这里简化实现，实际应使用 LangGraph 的 StateGraph 构建完整工作流
    # 以下为简化版本，直接按顺序执行

    print("=" * 60)
    print(f"任务：{task}")
    print(f"图片：{image_path}")
    print("=" * 60)

    # 步骤 1: Vision 分析
    print("\n[1/3] Vision Specialist 正在分析图片...")
    vision_analysis = analyze_with_vision(
        image_path,
        "请详细描述这张图片的内容，包括所有可见的组件、文字和关系。"
    )
    print(f"✓ Vision 分析完成\n{vision_analysis[:200]}...\n")

    # 步骤 2: Researcher 补充
    print("[2/3] Researcher 正在搜索背景知识...")
    # 实际中应调用 researcher_agent
    research_note = "[最佳实践] 请确保架构的可扩展性和可维护性"
    print(f"✓ Researcher 查找完成\n{research_note}\n")

    # 步骤 3: Writer 整合
    print("[3/3] Writer 正在整合输出...")
    final_prompt = f"""
    请整合以下信息，输出一份清晰的技术分析报告：

    【图片分析】
    {vision_analysis}

    【背景知识】
    {research_note}

    【用户任务】
    {task}

    要求：结构清晰、重点突出、专业准确。
    """

    final_output = text_llm.invoke([HumanMessage(content=final_prompt)]).content
    print("✓ 团队协作完成\n")

    return final_output


# ========== 示例场景 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("多模态研究团队 — Vision + Researcher + Writer")
    print("=" * 60)

    # 场景：分析系统架构图
    architecture_img = "system_arch.png"  # 替换为实际图片
    task = "分析这个系统架构的优缺点，并给出改进建议"

    print(f"\n📸 图片：{architecture_img}")
    print(f"📝 任务：{task}\n")

    try:
        result = run_vision_team_analysis(architecture_img, task)
        print("\n" + "=" * 60)
        print("📊 团队分析报告")
        print("=" * 60)
        print(result)
        print("=" * 60)
    except FileNotFoundError:
        print(f"[提示] 请准备图片 {architecture_img}")

    print("\n💡 提示：")
    print("1. 实际项目应使用 LangGraph StateGraph 构建完整工作流")
    print("2. 团队成员可并行执行部分任务，提升效率")
    print("3. 可根据任务复杂度动态增减团队成员")
