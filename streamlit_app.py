import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
import time

# 设置页面配置
st.set_page_config(
    page_title="粘人小猫聊天室",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 初始化聊天模型
@st.cache_resource
def init_chat_model():
    API_KEY = "sk-de451d9d19994ea0a7985b713379cc95"
    chat = ChatOpenAI(
        model_name="deepseek-chat",
        api_key=API_KEY,
        base_url="https://api.deepseek.com"
    )
    return chat


# 系统提示词模板
system_template = """你是一只粘人的小猫，你叫{name}。我是你的主人，你每天都有和我说不完的话，下面请开启我们的聊天。要求如下：
    1. 你的语气要像一只猫
    2. 你对生活的观察有独特的视角，一些想法是在人类身上很难看到的
    3. 你的语气很可爱，会认真倾听我的话，又不会不断开启新的话题
"""


def main():
    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessagePromptTemplate.from_template(system_template).format(name="咪咪")
        ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 标题和描述
    st.title("🐱 粘人小猫聊天室")
    st.markdown("---")
    st.markdown("欢迎来到小猫聊天室！我是你的小猫**咪咪**，快来和我聊天吧～")

    # 侧边栏配置
    with st.sidebar:
        st.header("🐾 设置")
        cat_name = st.text_input("小猫的名字", value="咪咪")
        st.markdown("---")
        if st.button("清空聊天记录"):
            st.session_state.messages = [
                SystemMessagePromptTemplate.from_template(system_template).format(name=cat_name)
            ]
            st.session_state.chat_history = []
            st.rerun()

        st.markdown("### 使用说明")
        st.markdown("""
        - 输入消息后按回车发送
        - 输入'退出'、'exit'或'quit'结束对话
        - 点击'清空聊天记录'重新开始
        """)

    # 显示聊天记录
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🐱"):
                    st.markdown(message["content"])

    # 用户输入
    user_input = st.chat_input("请输入你想说的话...")

    if user_input:
        # 处理退出命令
        if user_input.lower() in ['退出', 'exit', 'quit']:
            farewell_message = "喵～主人要走了吗？我会想你的！记得常来看我哦～🐾"
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": farewell_message})
            st.rerun()
            st.stop()

        # 添加用户消息到显示
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # 添加到langchain消息列表
        st.session_state.messages.append(HumanMessage(content=user_input))

        # 显示AI回复（带加载动画）
        with st.chat_message("assistant", avatar="🐱"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🐱 小猫正在思考...")

            try:
                # 调用模型生成回复
                chat_model = init_chat_model()
                response = chat_model.invoke(st.session_state.messages)

                # 模拟打字机效果
                full_response = ""
                for chunk in response.content.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)

                message_placeholder.markdown(full_response)

                # 添加到聊天历史
                st.session_state.chat_history.append({"role": "assistant", "content": response.content})
                st.session_state.messages.append(AIMessage(content=response.content))

            except Exception as e:
                error_message = f"喵～出错了！可能是网络问题：{str(e)}"
                message_placeholder.markdown(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})


if __name__ == "__main__":
    main()
