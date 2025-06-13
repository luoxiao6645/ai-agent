"""
简化版智能多模态AI Agent - Streamlit应用
"""
import streamlit as st
import os
import sys
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="智能多模态AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化OpenAI客户端
@st.cache_resource
def init_client():
    """初始化AI客户端"""
    try:
        client = OpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=os.getenv("ARK_API_KEY"),
        )
        return client
    except Exception as e:
        st.error(f"客户端初始化失败: {e}")
        return None

def main():
    """主界面"""
    st.title("🤖 智能多模态AI Agent系统")
    st.markdown("---")
    
    # 初始化客户端
    client = init_client()
    
    if not client:
        st.error("❌ AI客户端初始化失败，请检查API配置")
        return
    
    # 侧边栏
    with st.sidebar:
        st.header("🛠️ 系统控制")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ AI客户端已连接")
        st.info(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        
        # 模型配置
        st.subheader("⚙️ 模型配置")
        model = st.selectbox(
            "选择模型",
            [os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")],
            index=0
        )
        
        temperature = st.slider("温度", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("最大令牌数", 100, 2000, 500, 100)
        
        # 清除对话
        if st.button("🗑️ 清除对话"):
            st.session_state.messages = []
            st.rerun()
    
    # 主界面标签页
    tab1, tab2, tab3 = st.tabs(["💬 智能对话", "📁 文件处理", "🧮 工具箱"])
    
    with tab1:
        chat_interface(client, model, temperature, max_tokens)
    
    with tab2:
        file_interface(client, model)
    
    with tab3:
        tools_interface(client, model)

def chat_interface(client, model, temperature, max_tokens):
    """对话界面"""
    st.header("💬 智能对话")
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            with st.spinner("AI正在思考..."):
                try:
                    # 构建消息历史
                    messages = [
                        {"role": "system", "content": "你是豆包AI助手，一个智能、友好、有用的AI助手。"}
                    ]
                    messages.extend(st.session_state.messages)
                    
                    # 调用API
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    # 添加助手回复到历史
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    st.error(f"生成回复失败: {e}")

def file_interface(client, model):
    """文件处理界面"""
    st.header("📁 文件处理")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件", 
        type=['txt', 'md', 'json', 'csv'],
        help="支持文本文件、Markdown、JSON、CSV格式"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} 字节")
        
        # 读取文件内容
        try:
            if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.md'):
                content = uploaded_file.read().decode('utf-8')
            elif uploaded_file.name.endswith('.json'):
                import json
                content = json.dumps(json.load(uploaded_file), ensure_ascii=False, indent=2)
            elif uploaded_file.name.endswith('.csv'):
                content = uploaded_file.read().decode('utf-8')
            else:
                content = str(uploaded_file.read())
            
            # 显示文件内容预览
            st.subheader("📄 文件内容预览")
            st.text_area("内容", value=content[:1000] + "..." if len(content) > 1000 else content, height=200)
            
            # 文件分析选项
            st.subheader("🔍 文件分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 内容摘要"):
                    analyze_file_content(client, model, content, "请对以下文件内容进行摘要总结")
            
            with col2:
                if st.button("🔍 关键信息提取"):
                    analyze_file_content(client, model, content, "请提取以下文件内容中的关键信息")
            
        except Exception as e:
            st.error(f"文件读取失败: {e}")

def analyze_file_content(client, model, content, instruction):
    """分析文件内容"""
    with st.spinner("AI正在分析文件..."):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档分析助手。"},
                    {"role": "user", "content": f"{instruction}:\n\n{content[:3000]}"}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = response.choices[0].message.content
            st.success("✅ 分析完成")
            st.markdown("### 分析结果")
            st.markdown(result)
            
        except Exception as e:
            st.error(f"分析失败: {e}")

def tools_interface(client, model):
    """工具箱界面"""
    st.header("🧮 AI工具箱")
    
    # 工具选择
    tool_option = st.selectbox(
        "选择工具",
        ["💭 创意写作", "🔤 文本翻译", "📝 内容改写", "🧮 数学计算", "📊 数据分析"]
    )
    
    if tool_option == "💭 创意写作":
        creative_writing_tool(client, model)
    elif tool_option == "🔤 文本翻译":
        translation_tool(client, model)
    elif tool_option == "📝 内容改写":
        rewriting_tool(client, model)
    elif tool_option == "🧮 数学计算":
        math_tool(client, model)
    elif tool_option == "📊 数据分析":
        data_analysis_tool(client, model)

def creative_writing_tool(client, model):
    """创意写作工具"""
    st.subheader("💭 创意写作助手")
    
    writing_type = st.selectbox("写作类型", ["文章", "故事", "诗歌", "广告文案", "邮件"])
    topic = st.text_input("主题或关键词")
    style = st.selectbox("写作风格", ["正式", "轻松", "幽默", "专业", "创意"])
    length = st.selectbox("长度", ["简短", "中等", "详细"])
    
    if st.button("✨ 开始创作") and topic:
        with st.spinner("AI正在创作..."):
            try:
                prompt = f"请写一篇{style}风格的{writing_type}，主题是：{topic}。长度要求：{length}。"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的创意写作助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1000
                )
                
                result = response.choices[0].message.content
                st.success("✅ 创作完成")
                st.markdown("### 创作结果")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"创作失败: {e}")

def translation_tool(client, model):
    """翻译工具"""
    st.subheader("🔤 智能翻译")
    
    source_lang = st.selectbox("源语言", ["自动检测", "中文", "英文", "日文", "韩文", "法文", "德文"])
    target_lang = st.selectbox("目标语言", ["英文", "中文", "日文", "韩文", "法文", "德文"])
    
    text_to_translate = st.text_area("请输入要翻译的文本", height=150)
    
    if st.button("🔄 翻译") and text_to_translate:
        with st.spinner("AI正在翻译..."):
            try:
                prompt = f"请将以下文本从{source_lang}翻译为{target_lang}：\n\n{text_to_translate}"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的翻译助手，提供准确、自然的翻译。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                result = response.choices[0].message.content
                st.success("✅ 翻译完成")
                st.markdown("### 翻译结果")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"翻译失败: {e}")

def rewriting_tool(client, model):
    """内容改写工具"""
    st.subheader("📝 内容改写")
    
    rewrite_style = st.selectbox("改写风格", ["更正式", "更简洁", "更详细", "更通俗", "更专业"])
    original_text = st.text_area("请输入原始文本", height=150)
    
    if st.button("✏️ 改写") and original_text:
        with st.spinner("AI正在改写..."):
            try:
                prompt = f"请将以下文本改写得{rewrite_style}：\n\n{original_text}"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的文本编辑助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=800
                )
                
                result = response.choices[0].message.content
                st.success("✅ 改写完成")
                st.markdown("### 改写结果")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"改写失败: {e}")

def math_tool(client, model):
    """数学计算工具"""
    st.subheader("🧮 数学计算助手")
    
    math_problem = st.text_area("请输入数学问题或计算表达式", height=100)
    
    if st.button("🔢 计算") and math_problem:
        with st.spinner("AI正在计算..."):
            try:
                prompt = f"请解决以下数学问题，提供详细的解题步骤：\n\n{math_problem}"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的数学助手，擅长解决各种数学问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=800
                )
                
                result = response.choices[0].message.content
                st.success("✅ 计算完成")
                st.markdown("### 计算结果")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"计算失败: {e}")

def data_analysis_tool(client, model):
    """数据分析工具"""
    st.subheader("📊 数据分析助手")
    
    data_input = st.text_area("请输入数据（支持CSV格式或描述数据）", height=150)
    analysis_type = st.selectbox("分析类型", ["基础统计", "趋势分析", "数据总结", "异常检测"])
    
    if st.button("📈 分析") and data_input:
        with st.spinner("AI正在分析数据..."):
            try:
                prompt = f"请对以下数据进行{analysis_type}：\n\n{data_input}"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的数据分析师，擅长数据分析和解释。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                result = response.choices[0].message.content
                st.success("✅ 分析完成")
                st.markdown("### 分析结果")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"分析失败: {e}")

if __name__ == "__main__":
    main()
