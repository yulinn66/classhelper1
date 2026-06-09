# -*- coding: utf-8 -*-
"""
Python 闯关学习游戏 - Streamlit 应用
包含闯关游戏和题目管理两大功能，支持动态添加/编辑/删除关卡。
"""

import streamlit as st

# ============================================================
# 默认关卡数据（初始化用）
# ============================================================
DEFAULT_LEVELS = [
    {
        "title": "第一关: 变量与类型",
        "question": "在 Python 中，以下哪个是合法的变量名?",
        "options": ["1var", "var_name", "var-name", "for"],
        "answer": "var_name",
        "reward": "🏅 变量小能手"
    },
    {
        "title": "第二关: 条件判断",
        "question": "以下代码输出什么?\n\npython\nx = 5\nif x > 3:\n    print('A')\nelse:\n    print('B')\n",
        "options": ["A", "B", "报错", "无输出"],
        "answer": "A",
        "reward": "🏅 条件判断大师"
    },
    {
        "title": "第三关: 循环入门",
        "question": "以下代码会打印几次 'Hello'?\n\npython\nfor i in range(3):\n    print('Hello')\n",
        "options": ["1次", "2次", "3次", "无限次"],
        "answer": "3次",
        "reward": "🏅 循环征服者"
    }
]

TOTAL_LEVELS = len(DEFAULT_LEVELS)
POINTS_PER_LEVEL = 10


# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="Python 闯关游戏",
    page_icon="🎮",
    layout="centered"
)


# ============================================================
# session_state 初始化
# ============================================================
# levels: 存储所有关卡的列表
if "levels" not in st.session_state:
    st.session_state.levels = [level.copy() for level in DEFAULT_LEVELS]

# current_level: 当前关卡索引（从0开始）
if "current_level" not in st.session_state:
    st.session_state.current_level = 0

# score: 当前得分
if "score" not in st.session_state:
    st.session_state.score = 0

# badges: 已获得的徽章列表
if "badges" not in st.session_state:
    st.session_state.badges = []


# ============================================================
# 辅助函数
# ============================================================
def reset_game():
    """重置游戏状态（回到第一关、得分清零、徽章清空）"""
    st.session_state.current_level = 0
    st.session_state.score = 0
    st.session_state.badges = []
    st.rerun()


def reset_to_default_levels():
    """重置关卡列表为默认题目，并重置游戏"""
    st.session_state.levels = [level.copy() for level in DEFAULT_LEVELS]
    reset_game()


def check_and_fix_index():
    """检查当前关卡索引是否越界，如果越界则重置游戏"""
    if st.session_state.current_level >= len(st.session_state.levels):
        reset_game()


# ============================================================
# 侧边栏：题目管理
# ============================================================
with st.sidebar:
    st.header("📝 题目管理")
    st.markdown("---")

    # ---- 功能选择 ----
    manager_mode = st.radio(
        "选择操作",
        ["添加新关卡", "编辑/删除关卡", "重置默认题目"],
        label_visibility="collapsed"
    )

    # ============================================================
    # 添加新关卡
    # ============================================================
    if manager_mode == "添加新关卡":
        st.subheader("添加新关卡")

        new_title = st.text_input("关卡标题", placeholder="例如: 第四关: 函数基础")
        new_question = st.text_area(
            "问题描述（支持 Markdown）",
            placeholder="输入问题内容，可以用 python 代码 包含代码块",
            height=120
        )

        st.markdown("**四个选项**")
        col1, col2 = st.columns(2)
        with col1:
            opt_a = st.text_input("选项 A", key="opt_a")
            opt_b = st.text_input("选项 B", key="opt_b")
        with col2:
            opt_c = st.text_input("选项 C", key="opt_c")
            opt_d = st.text_input("选项 D", key="opt_d")

        new_answer = st.text_input(
            "正确答案（必须与上面某个选项完全一致）",
            placeholder="例如: A"
        )
        new_reward = st.text_input(
            "徽章名称",
            placeholder="例如: 🏅 函数小能手"
        )

        if st.button("添加关卡", type="primary", use_container_width=True):
            # 验证必填项
            if not new_title or not new_question or not new_answer:
                st.error("请填写标题、问题和答案!")
            elif not all([opt_a, opt_b, opt_c, opt_d]):
                st.error("请填写全部四个选项!")
            elif new_answer not in [opt_a, opt_b, opt_c, opt_d]:
                st.error("正确答案必须与四个选项之一完全一致!")
            else:
                # 添加新关卡
                new_level = {
                    "title": new_title,
                    "question": new_question,
                    "options": [opt_a, opt_b, opt_c, opt_d],
                    "answer": new_answer,
                    "reward": new_reward if new_reward else "🏅 新徽章"
                }
                st.session_state.levels.append(new_level)
                st.success(f"已添加新关卡: {new_title}")
                st.rerun()

    # ============================================================
    # 编辑/删除现有关卡
    # ============================================================
    elif manager_mode == "编辑/删除关卡":
        st.subheader("编辑或删除关卡")

        if len(st.session_state.levels) == 0:
            st.warning("暂无关卡，请先添加!")
        else:
            # 选择要编辑的关卡
            level_titles = [f"关卡 {i+1}: {lv['title']}" for i, lv in enumerate(st.session_state.levels)]
            selected_idx = st.selectbox(
                "选择关卡",
                range(len(level_titles)),
                format_func=lambda x: level_titles[x],
                key="edit_select"
            )

            level = st.session_state.levels[selected_idx]

            # 编辑表单
            st.markdown("---")
            st.markdown("**修改关卡内容**")

            edit_title = st.text_input("标题", value=level["title"], key="edit_title")
            edit_question = st.text_area(
                "问题描述（支持 Markdown）",
                value=level["question"],
                height=120,
                key="edit_question"
            )

            st.markdown("**四个选项**")
            col1, col2 = st.columns(2)
            with col1:
                edit_opt_a = st.text_input("选项 A", value=level["options"][0], key="edit_opt_a")
                edit_opt_b = st.text_input("选项 B", value=level["options"][1], key="edit_opt_b")
            with col2:
                edit_opt_c = st.text_input("选项 C", value=level["options"][2], key="edit_opt_c")
                edit_opt_d = st.text_input("选项 D", value=level["options"][3], key="edit_opt_d")

            edit_answer = st.text_input(
                "正确答案",
                value=level["answer"],
                key="edit_answer"
            )
            edit_reward = st.text_input(
                "徽章名称",
                value=level["reward"],
                key="edit_reward"
            )

            col_save, col_delete = st.columns(2)

            with col_save:
                if st.button("保存修改", type="primary", use_container_width=True):
                    if not edit_title or not edit_question or not edit_answer:
                        st.error("请填写标题、问题和答案!")
                    elif edit_answer not in [edit_opt_a, edit_opt_b, edit_opt_c, edit_opt_d]:
                        st.error("正确答案必须与四个选项之一完全一致!")
                    else:
                        st.session_state.levels[selected_idx] = {
                            "title": edit_title,
                            "question": edit_question,
                            "options": [edit_opt_a, edit_opt_b, edit_opt_c, edit_opt_d],
                            "answer": edit_answer,
                            "reward": edit_reward if edit_reward else "🏅 新徽章"
                        }
                        st.success("修改已保存!")
                        st.rerun()

            with col_delete:
                if st.button("删除此关卡", use_container_width=True):
                    deleted_title = st.session_state.levels[selected_idx]["title"]
                    del st.session_state.levels[selected_idx]
                    st.warning(f"已删除: {deleted_title}")
                    # 如果删除了当前关卡之后的关卡，导致索引越界，则重置游戏
                    if st.session_state.current_level >= len(st.session_state.levels):
                        st.session_state.current_level = 0
                        st.session_state.score = 0
                        st.session_state.badges = []
                    st.rerun()

    # ============================================================
    # 重置为默认题目
    # ============================================================
    elif manager_mode == "重置默认题目":
        st.subheader("重置默认题目")
        st.markdown("将关卡列表恢复为最初的 3 个示例题目，并重置游戏进度。")
        st.warning("此操作会覆盖当前所有自定义关卡!")

        if st.button("确认重置", type="primary", use_container_width=True):
            reset_to_default_levels()

    st.markdown("---")

    # ---- 游戏控制 ----
    st.header("🎮 游戏控制")
    if st.button("重新开始", use_container_width=True):
        reset_game()

    st.markdown("---")
    st.markdown(f"当前关卡数: {len(st.session_state.levels)}")


# ============================================================
# 主页面：闯关游戏
# ============================================================

# 页面标题
st.title("🎮 Python 闯关游戏")
st.markdown("---")

# 顶部信息栏
current_idx = st.session_state.current_level
levels_count = len(st.session_state.levels)

# 进度条
if levels_count > 0:
    progress_ratio = current_idx / levels_count
    st.progress(progress_ratio, text=f"关卡进度: 第 {current_idx} / {levels_count} 关")
else:
    st.progress(0, text="关卡进度: 0 / 0 关")

# 得分和徽章
col1, col2 = st.columns(2)
with col1:
    st.metric(label="当前得分", value=f"{st.session_state.score} 分")
with col2:
    st.markdown("**🏅 已获徽章**")
    if st.session_state.badges:
        for badge in st.session_state.badges:
            st.markdown(f"    {badge}")
    else:
        st.markdown("    暂无徽章")

st.markdown("---")


# ============================================================
# 游戏主体逻辑
# ============================================================

# 检查是否有关卡
if levels_count == 0:
    # 无关卡时显示提示
    st.info("暂无题目，请在左侧题目管理中添加关卡!")
    st.markdown("---")
    st.markdown("点击侧边栏添加新关卡开始创建题目!")

elif st.session_state.current_level >= levels_count:
    # ---- 通关画面 ----
    st.balloons()
    st.success("🎉 恭喜通关! 🎉", icon="✅")
    st.markdown(f"""
    ### 游戏完成总结
    - **最终得分**: {st.session_state.score} 分（满分 {levels_count * POINTS_PER_LEVEL} 分）
    - **获得徽章**: {len(st.session_state.badges)} 个
    """)
    if st.session_state.badges:
        st.markdown("**徽章墙:**")
        cols = st.columns(len(st.session_state.badges))
        for i, badge in enumerate(st.session_state.badges):
            with cols[i]:
                st.markdown(f"<h3 style='text-align: center;'>{badge}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("点击侧边栏重新开始按钮可以再来一轮!")

else:
    # ---- 当前关卡内容 ----
    level = st.session_state.levels[current_idx]

    # 关卡标题
    st.subheader(f"### {level['title']}")

    # 问题描述（支持 Markdown 和代码块）
    st.markdown("**问题:**")
    st.markdown(level["question"])

    # 选项列表
    st.markdown("**请选择答案:**")

    # 确保 radio 的 index 有效
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None

    selected = st.radio(
        label="选项",
        options=level["options"],
        index=0,
        label_visibility="collapsed"
    )

    # 提交按钮
    st.markdown("")
    if st.button("提交答案", type="primary", use_container_width=True):
        if selected == level["answer"]:
            # ---- 答对 ----
            st.success("🎊 回答正确!", icon="✅")

            # 增加得分
            st.session_state.score += POINTS_PER_LEVEL

            # 获得徽章
            reward = level["reward"]
            if reward not in st.session_state.badges:
                st.session_state.badges.append(reward)

            # 显示获得徽章提示
            st.info(f"恭喜获得: {reward}")

            # 进入下一关
            st.session_state.current_level += 1
            st.rerun()
        else:
            # ---- 答错 ----
            st.error("回答错误，请重新选择答案!", icon="🚫")
            st.warning("提示: 仔细想想，再试一次 😊")
