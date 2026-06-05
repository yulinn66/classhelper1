"""
Python 闯关学习游戏 - Streamlit 应用
一个基于选择题的闯关式学习游戏，包含3个关卡，支持得分、徽章和进度追踪。
"""

import streamlit as st

# ============================================================
# 1. 关卡数据结构定义
# ============================================================
# 每个关卡包含：标题、问题描述、选项列表、正确答案、徽章名称
LEVELS = [
    {
        "title": "第一关：变量与类型",
        "question": "在 Python 中，以下哪个是合法的变量名？",
        "options": ["1var", "var_name", "var-name", "for"],
        "answer": "var_name",
        "badge": "🏅 变量小能手"
    },
    {
        "title": "第二关：条件判断",
        "question": """以下代码输出什么？

```python
x = 5
if x > 3:
    print('A')
else:
    print('B')
```""",
        "options": ["A", "B", "报错", "无输出"],
        "answer": "A",
        "badge": "🏅 条件判断大师"
    },
    {
        "title": "第三关：循环入门",
        "question": """以下代码会打印几次 'Hello'？

```python
for i in range(3):
    print('Hello')
```""",
        "options": ["1次", "2次", "3次", "无限次"],
        "answer": "3次",
        "badge": "🏅 循环征服者"
    }
]

TOTAL_LEVELS = len(LEVELS)
POINTS_PER_LEVEL = 10  # 每关得分


# ============================================================
# 2. 页面配置与初始化
# ============================================================
st.set_page_config(
    page_title="Python 闯关游戏",
    page_icon="🎮",
    layout="centered"
)

# 初始化 session_state（仅在首次运行时执行）
if "current_level" not in st.session_state:
    st.session_state.current_level = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "badges" not in st.session_state:
    st.session_state.badges = []
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None


# ============================================================
# 3. 重置游戏函数
# ============================================================
def reset_game():
    """重置所有游戏状态，回到第一关"""
    st.session_state.current_level = 0
    st.session_state.score = 0
    st.session_state.badges = []
    st.session_state.selected_option = None
    st.rerun()


# ============================================================
# 4. 主页面布局
# ============================================================

# 页面标题
st.title("🎮 Python 闯关游戏")
st.markdown("---")

# ---- 侧边栏：重新开始按钮 ----
with st.sidebar:
    st.header("📌 游戏控制")
    if st.button("🔄 重新开始", use_container_width=True):
        reset_game()
    st.markdown("---")
    st.markdown("**🎯 游戏规则**")
    st.markdown("""
    - 共 3 个关卡
    - 每关 10 分，答对自动进入下一关
    - 答错可以重新选择答案
    - 全部通关可获得气球庆祝！
    """)

# ---- 顶部信息栏：进度条、得分、徽章 ----
current_idx = st.session_state.current_level
progress_ratio = current_idx / TOTAL_LEVELS
st.progress(progress_ratio, text=f"关卡进度：第 {current_idx} / {TOTAL_LEVELS} 关")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📊 当前得分", value=f"{st.session_state.score} 分")
with col2:
    st.markdown("**🏅 已获徽章**")
    if st.session_state.badges:
        for badge in st.session_state.badges:
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{badge}")
    else:
        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;*暂无徽章*")

st.markdown("---")

# ============================================================
# 5. 判断是否已通关
# ============================================================
if st.session_state.current_level >= TOTAL_LEVELS:
    # ---- 通关画面 ----
    st.balloons()
    st.success("🎉 **恭喜通关！** 🎉", icon="✅")
    st.markdown(f"""
    ### 游戏完成总结
    - **最终得分**：{st.session_state.score} 分（满分 {TOTAL_LEVELS * POINTS_PER_LEVEL} 分）
    - **获得徽章**：{len(st.session_state.badges)} 个
    """)
    if st.session_state.badges:
        st.markdown("**徽章墙：**")
        cols = st.columns(len(st.session_state.badges))
        for i, badge in enumerate(st.session_state.badges):
            with cols[i]:
                st.markdown(f"<h3 style='text-align: center;'>{badge}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("👈 点击侧边栏「重新开始」按钮可以再来一轮！")

else:
    # ---- 当前关卡内容 ----
    level = LEVELS[current_idx]
    
    # 关卡标题
    st.subheader(f"### {level['title']}")
    
    # 问题描述（支持 Markdown 和代码块）
    st.markdown("**问题：**")
    st.markdown(level["question"])
    
    # 选项列表
    st.markdown("**请选择答案：**")
    selected = st.radio(
        label="选项",
        options=level["options"],
        index=level["options"].index(st.session_state.selected_option) if st.session_state.selected_option in level["options"] else 0,
        key=f"radio_{current_idx}",
        label_visibility="collapsed"
    )
    st.session_state.selected_option = selected
    
    # 提交按钮
    st.markdown("")
    if st.button("✅ 提交答案", type="primary", use_container_width=True):
        if selected == level["answer"]:
            # ---- 答对 ----
            st.success("🎊 回答正确！", icon="✅")
            
            # 增加得分
            st.session_state.score += POINTS_PER_LEVEL
            
            # 获得徽章
            badge = level["badge"]
            if badge not in st.session_state.badges:
                st.session_state.badges.append(badge)
            
            # 显示获得徽章提示
            st.info(f"恭喜获得：{badge}")
            
            # 进入下一关
            st.session_state.current_level += 1
            st.session_state.selected_option = None
            
            # 短暂提示后自动跳转
            st.rerun()
        else:
            # ---- 答错 ----
            st.error("❌ 回答错误，请重新选择答案！", icon="🚫")
            st.warning("提示：仔细想想，再试一次 😊")
