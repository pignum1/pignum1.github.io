"""
AI-Python-09.1 实战 1: 图片理解基础
三种场景：自然场景描述、架构图理解、OCR 文字识别
"""

import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# GLM-4V-Flash 配置（通过 OpenAI 兼容接口调用）
# 请替换为你的实际 API Key
vision_llm = ChatOpenAI(
    model="glm-4v-flash",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key="your-api-key-here",
    temperature=0.3
)


def analyze_image_url(image_url: str, prompt: str) -> str:
    """分析 URL 图片"""
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    )
    response = vision_llm.invoke([message])
    return response.content


def analyze_image_base64(image_path: str, prompt: str) -> str:
    """分析本地 base64 图片"""
    # 判断图片类型
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"  # 默认

    # 编码为 base64
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
        ]
    )
    response = vision_llm.invoke([message])
    return response.content


# 场景 A：自然场景描述（URL 图片）
def scenario_a_natural_scene():
    """分析自然场景图片"""
    print("=" * 50)
    print("场景 A：自然场景描述")
    print("=" * 50)

    # 使用示例 URL（可替换为任意公网图片）
    image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

    prompt = "请详细描述这张图片中的场景，包括：1) 主要物体 2) 环境氛围 3) 色彩搭配 4) 你的主观感受"

    result = analyze_image_url(image_url, prompt)
    print(f"\n分析结果：\n{result}\n")


# 场景 B：架构图理解（本地 base64 图片）
def scenario_b_architecture_diagram():
    """理解系统架构图"""
    print("=" * 50)
    print("场景 B：架构图理解")
    print("=" * 50)

    # 假设有一张本地架构图：architecture.png
    image_path = "architecture.png"

    prompt = """
    请分析这张系统架构图：
    1. 有哪些主要组件？
    2. 组件之间的调用关系是什么？
    3. 数据流向如何？
    4. 这个架构的核心设计思想是什么？
    5. 有没有潜在的性能瓶颈或单点故障？
    """

    try:
        result = analyze_image_base64(image_path, prompt)
        print(f"\n分析结果：\n{result}\n")
    except FileNotFoundError:
        print(f"\n[提示] 请准备一张架构图命名为 {image_path}，或替换为实际图片路径\n")


# 场景 C：OCR 文字识别
def scenario_c_ocr():
    """识别图片中的文字"""
    print("=" * 50)
    print("场景 C：OCR 文字识别")
    print("=" * 50)

    # 假设有一张含文字的图片：document.jpg
    image_path = "document.jpg"

    prompt = """
    请识别这张图片中的所有文字内容：
    1. 提取所有可见文字
    2. 保持原有格式和层级结构
    3. 如果是表格，请用 Markdown 表格格式输出
    4. 如果有公式，请用 LaTeX 格式输出
    """

    try:
        result = analyze_image_base64(image_path, prompt)
        print(f"\n识别结果：\n{result}\n")
    except FileNotFoundError:
        print(f"\n[提示] 请准备一张含文字的图片命名为 {image_path}，或替换为实际图片路径\n")


if __name__ == "__main__":
    # 执行三个场景
    scenario_a_natural_scene()
    scenario_b_architecture_diagram()
    scenario_c_ocr()

    print("\n" + "=" * 50)
    print("💡 提示：")
    print("1. 场景 A 使用公网 URL，需确保网络可访问")
    print("2. 场景 B 和 C 需要准备本地图片，或修改 image_path 为实际路径")
    print("3. GLM-4V-Flash 免费额度有限，注意控制调用次数")
    print("=" * 50)
