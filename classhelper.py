# -*- coding: utf-8 -*-
"""
Python 闯关学习游戏 - Streamlit 应用
========================================
这是一个基于 Streamlit 框架开发的 Python 学习闯关游戏应用。

主要功能：
1. 闯关游戏：用户答题闯关，获得分数和徽章奖励
2. 题目管理：支持动态添加、编辑、删除关卡题目

游戏规则：
- 每道题有 2 次尝试机会
- 第一次答错：提示错误，允许再试一次（不显示正确答案）
- 第二次答错：显示正确答案，不得分，进入下一题
- 答对：获得 10 分和对应徽章，进入下一题
- 通关后显示总分和徽章墙

技术要点：
- 使用 st.session_state 管理游戏状态（关卡进度、得分、徽章等）
- 使用 st.container 实现卡片式布局
- 支持 Markdown 格式的题目描述
"""

import streamlit as st

# ============================================================
# 默认关卡数据（初始化用）
# ============================================================
# 这是一个关卡列表，每个关卡是一个字典，包含以下字段：
# - title: 关卡标题（字符串）
# - question: 问题描述（字符串，支持 Markdown 格式）
# - options: 四个选项的列表（列表）
# - answer: 正确答案（字符串，必须与 options 中的某一项完全一致）
# - reward: 徽章奖励名称（字符串）
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

# 游戏配置常量
TOTAL_LEVELS = len(DEFAULT_LEVELS)  # 默认关卡总数（用于初始化）
POINTS_PER_LEVEL = 10               # 每道题的分数


# ============================================================
# 页面配置
# ============================================================
# st.set_page_config() 必须是页面中的第一个 Streamlit 命令
# 用于设置页面的标题、图标和布局方式
st.set_page_config(
    page_title="Python 闯关游戏",   # 浏览器标签页标题
    page_icon="🎮",                  # 浏览器标签页图标
    layout="centered"                # 页面布局：centered（居中）或 wide（宽屏）
)


# ============================================================
# session_state 初始化
# ============================================================
# st.session_state 是 Streamlit 提供的状态管理机制
# 用于在页面刷新（rerun）之间保持数据
# 每个状态变量都需要在使用前检查是否存在，不存在则初始化

# levels: 存储所有关卡的列表
# 用户可以动态添加、编辑、删除关卡，所以需要保存在 session_state 中
if "levels" not in st.session_state:
    # 使用 level.copy() 创建关卡副本，避免修改默认数据
    st.session_state.levels = [level.copy() for level in DEFAULT_LEVELS]

# current_level: 当前关卡索引（从 0 开始）
# 表示用户正在回答第几题
if "current_level" not in st.session_state:
    st.session_state.current_level = 0

# score: 当前得分
# 每答对一题加 POINTS_PER_LEVEL 分
if "score" not in st.session_state:
    st.session_state.score = 0

# badges: 已获得的徽章列表
# 存储用户获得的徽章名称，避免重复获得同一徽章
if "badges" not in st.session_state:
    st.session_state.badges = []

# selected_option: 当前选中的答案选项
# 用于在页面刷新后保持用户的选项选择状态
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# wrong_attempts: 当前关卡错误尝试次数
# 每道题最多允许答错 2 次
if "wrong_attempts" not in st.session_state:
    st.session_state.wrong_attempts = 0

# show_result: 是否显示答案结果
# True 表示进入答案展示环节，False 表示处于答题环节
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# is_correct: 上一次提交的答案是否正确
# 用于在答案展示环节显示不同的提示信息
if "is_correct" not in st.session_state:
    st.session_state.is_correct = False

# earned_reward: 本次答对获得的徽章名称
# 用于在答案展示环节显示获得的徽章
if "earned_reward" not in st.session_state:
    st.session_state.earned_reward = None

# success_message: 成功提示消息
# 用于在页面刷新后显示操作成功的提示
if "success_message" not in st.session_state:
    st.session_state.success_message = None


# ============================================================
# 辅助函数
# ============================================================
def reset_game():
    """
    重置游戏状态
    
    将游戏恢复到初始状态：
    - 回到第一关（current_level = 0）
    - 得分清零（score = 0）
    - 徽章清空（badges = []）
    - 错误次数清零（wrong_attempts = 0）
    - 隐藏答案结果（show_result = False）
    - 清空选中选项（selected_option = None）
    
    调用 st.rerun() 刷新页面以应用更改
    """
    st.session_state.current_level = 0
    st.session_state.score = 0
    st.session_state.badges = []
    st.session_state.wrong_attempts = 0
    st.session_state.show_result = False
    st.session_state.selected_option = None
    st.rerun()


def reset_to_default_levels():
    """
    重置关卡列表为默认题目，并重置游戏
    
    将关卡列表恢复为 DEFAULT_LEVELS 中定义的默认题目
    同时调用 reset_game() 重置游戏进度
    用于用户想要重新开始或恢复默认题目时
    """
    st.session_state.levels = [level.copy() for level in DEFAULT_LEVELS]
    reset_game()


def check_and_fix_index():
    """
    检查当前关卡索引是否越界
    
    如果当前关卡索引 >= 关卡总数，说明用户已完成所有关卡
    此时调用 reset_game() 重置游戏
    
    注意：这个函数目前未被使用，但保留以备将来扩展
    """
    if st.session_state.current_level >= len(st.session_state.levels):
        reset_game()


# ============================================================
# 侧边栏：题目管理
# ============================================================
# 使用 with st.sidebar 将内容放在侧边栏中
# 侧边栏用于题目管理功能和游戏控制
with st.sidebar:
    # 侧边栏标题
    st.header("📝 题目管理")
    st.markdown("---")

    # ---- 功能选择 ----
    # 使用 radio 按钮让用户选择要执行的操作
    # label_visibility="collapsed" 隐藏标签，只显示选项
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

        # 关卡标题输入框
        # placeholder 提供输入示例
        new_title = st.text_input("关卡标题", placeholder="例如: 第四关: 函数基础")
        
        # 问题描述输入框
        # text_area 用于多行文本输入，height 设置高度
        new_question = st.text_area(
            "问题描述（支持 Markdown）",
            placeholder="输入问题内容，可以用 ```python 代码 ``` 包含代码块",
            height=120
        )

        # 四个选项输入框，使用两列布局
        st.markdown("**四个选项**")
        col1, col2 = st.columns(2)  # 创建两列布局
        with col1:
            opt_a = st.text_input("选项 A", key="opt_a")  # key 用于区分不同的输入框
            opt_b = st.text_input("选项 B", key="opt_b")
        with col2:
            opt_c = st.text_input("选项 C", key="opt_c")
            opt_d = st.text_input("选项 D", key="opt_d")

        # 正确答案输入框
        # 提醒用户答案必须与选项完全一致
        new_answer = st.text_input(
            "正确答案（必须与上面某个选项完全一致）",
            placeholder="例如: A"
        )
        
        # 徽章名称输入框
        new_reward = st.text_input(
            "徽章名称",
            placeholder="例如: 🏅 函数小能手"
        )

        # 添加关卡按钮
        # type="primary" 使按钮更醒目
        # use_container_width=True 使按钮占满容器宽度
        if st.button("添加关卡", type="primary", use_container_width=True):
            # 验证必填项是否填写
            if not new_title or not new_question or not new_answer:
                st.error("请填写标题、问题和答案!")
            # 验证四个选项是否都填写了
            elif not all([opt_a, opt_b, opt_c, opt_d]):
                st.error("请填写全部四个选项!")
            # 验证正确答案是否在选项中
            elif new_answer not in [opt_a, opt_b, opt_c, opt_d]:
                st.error("正确答案必须与四个选项之一完全一致!")
            else:
                # 所有验证通过，创建新关卡字典
                new_level = {
                    "title": new_title,
                    "question": new_question,
                    "options": [opt_a, opt_b, opt_c, opt_d],
                    "answer": new_answer,
                    "reward": new_reward if new_reward else "🏅 新徽章"  # 默认徽章名称
                }
                # 将新关卡添加到关卡列表
                st.session_state.levels.append(new_level)
                # 设置成功消息，刷新后显示
                st.session_state.success_message = f"✅ 已添加新关卡: {new_title}"
                # 刷新页面以显示新添加的关卡
                st.rerun()

        # 显示成功消息（在添加关卡按钮下方）
        if st.session_state.success_message:
            st.success(st.session_state.success_message)
            st.session_state.success_message = None  # 显示后清除消息

    # ============================================================
    # 编辑/删除现有关卡
    # ============================================================
    elif manager_mode == "编辑/删除关卡":
        st.subheader("编辑或删除关卡")

        # 检查是否有关卡可编辑
        if len(st.session_state.levels) == 0:
            st.warning("暂无关卡，请先添加!")
        else:
            # 创建关卡选择下拉框
            # 格式化为 "关卡 1: 第一关标题" 的形式
            level_titles = [f"关卡 {i+1}: {lv['title']}" for i, lv in enumerate(st.session_state.levels)]
            selected_idx = st.selectbox(
                "选择关卡",
                range(len(level_titles)),  # 选项值为索引
                format_func=lambda x: level_titles[x],  # 显示格式化后的标题
                key="edit_select"
            )

            # 获取选中的关卡数据
            level = st.session_state.levels[selected_idx]

            # 编辑表单
            st.markdown("---")
            st.markdown("**修改关卡内容**")

            # 预填充当前关卡的数据
            # 使用动态 key（包含 selected_idx），确保选择关卡时组件会重新创建并显示新内容
            edit_title = st.text_input("标题", value=level["title"], key=f"edit_title_{selected_idx}")
            edit_question = st.text_area(
                "问题描述（支持 Markdown）",
                value=level["question"],
                height=120,
                key=f"edit_question_{selected_idx}"
            )

            # 四个选项编辑框
            st.markdown("**四个选项**")
            col1, col2 = st.columns(2)
            with col1:
                edit_opt_a = st.text_input("选项 A", value=level["options"][0], key=f"edit_opt_a_{selected_idx}")
                edit_opt_b = st.text_input("选项 B", value=level["options"][1], key=f"edit_opt_b_{selected_idx}")
            with col2:
                edit_opt_c = st.text_input("选项 C", value=level["options"][2], key=f"edit_opt_c_{selected_idx}")
                edit_opt_d = st.text_input("选项 D", value=level["options"][3], key=f"edit_opt_d_{selected_idx}")

            # 正确答案和徽章编辑框
            edit_answer = st.text_input(
                "正确答案",
                value=level["answer"],
                key=f"edit_answer_{selected_idx}"
            )
            edit_reward = st.text_input(
                "徽章名称",
                value=level["reward"],
                key=f"edit_reward_{selected_idx}"
            )

            # 保存和删除按钮，使用两列布局
            col_save, col_delete = st.columns(2)

            # 保存修改按钮
            with col_save:
                if st.button("保存修改", type="primary", use_container_width=True):
                    # 验证必填项
                    if not edit_title or not edit_question or not edit_answer:
                        st.error("请填写标题、问题和答案!")
                    # 验证答案是否在选项中
                    elif edit_answer not in [edit_opt_a, edit_opt_b, edit_opt_c, edit_opt_d]:
                        st.error("正确答案必须与四个选项之一完全一致!")
                    else:
                        # 更新关卡数据
                        st.session_state.levels[selected_idx] = {
                            "title": edit_title,
                            "question": edit_question,
                            "options": [edit_opt_a, edit_opt_b, edit_opt_c, edit_opt_d],
                            "answer": edit_answer,
                            "reward": edit_reward if edit_reward else "🏅 新徽章"
                        }
                        st.success("修改已保存!")
                        st.rerun()

            # 删除关卡按钮
            with col_delete:
                if st.button("删除此关卡", use_container_width=True):
                    # 记录被删除的关卡标题
                    deleted_title = st.session_state.levels[selected_idx]["title"]
                    # 从列表中删除关卡
                    del st.session_state.levels[selected_idx]
                    st.warning(f"已删除: {deleted_title}")
                    
                    # 检查删除后是否导致当前关卡索引越界
                    # 如果当前关卡索引 >= 关卡总数，则重置游戏
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

        # 确认重置按钮
        if st.button("确认重置", type="primary", use_container_width=True):
            reset_to_default_levels()

    st.markdown("---")

    # ---- 游戏控制 ----
    st.header("🎮 游戏控制")
    # 重新开始按钮，重置游戏进度
    if st.button("重新开始", use_container_width=True):
        reset_game()

    st.markdown("---")
    # 显示当前关卡总数
    st.markdown(f"当前关卡数: {len(st.session_state.levels)}")


# ============================================================
# 主页面：闯关游戏
# ============================================================

# 页面标题
st.title("🎮 Python 闯关游戏")
st.markdown("---")

# 顶部信息栏
# 获取当前关卡索引和关卡总数
current_idx = st.session_state.current_level
levels_count = len(st.session_state.levels)

# 进度条（从1开始显示，更符合用户习惯）
# progress_ratio = 当前关卡索引 / 关卡总数
if levels_count > 0:
    progress_ratio = current_idx / levels_count
    # 显示格式：第 X / Y 关（X 从 1 开始）
    st.progress(progress_ratio, text=f"关卡进度: 第 {current_idx + 1} / {levels_count} 关")
else:
    # 没有关卡时显示 0/0
    st.progress(0, text="关卡进度: 0 / 0 关")

# 得分和徽章展示
# 使用两列布局
col1, col2 = st.columns(2)
with col1:
    # 显示当前得分
    st.metric(label="当前得分", value=f"{st.session_state.score} 分")
with col2:
    # 显示已获得的徽章
    st.markdown("**🏅 已获徽章**")
    if st.session_state.badges:
        # 将所有徽章横向排列显示
        st.markdown(" ".join([f"**{badge}**" for badge in st.session_state.badges]))
    else:
        st.markdown("暂无徽章")

st.markdown("---")


# ============================================================
# 游戏主体逻辑
# ============================================================

# 检查是否有关卡
if levels_count == 0:
    # 无关卡时显示提示信息
    st.info("暂无题目，请在左侧题目管理中添加关卡!")
    st.markdown("---")
    st.markdown("点击侧边栏添加新关卡开始创建题目!")

elif st.session_state.current_level >= levels_count:
    # ---- 通关画面 ----
    # 当 current_level >= levels_count 时，说明用户已完成所有关卡
    
    # 显示气球动画庆祝
    st.balloons()
    
    # 使用容器包装通关信息，带边框效果
    with st.container(border=True):
        st.success("🎉 恭喜通关! 🎉", icon="✅")
        
        # 显示游戏完成总结
        st.markdown(f"""
        ### 游戏完成总结
        - **总分**: {levels_count * 10} 分（假设所有题目一次答对）
        - **你的得分**: {st.session_state.score} 分
        - **获得徽章**: {len(st.session_state.badges)} 个
        """)
        
        # 如果有徽章，显示徽章墙
        if st.session_state.badges:
            st.markdown("**徽章墙:**")
            # 每个徽章占一列，居中显示
            cols = st.columns(len(st.session_state.badges))
            for i, badge in enumerate(st.session_state.badges):
                with cols[i]:
                    # 使用 HTML 实现居中对齐
                    st.markdown(f"<h3 style='text-align: center;'>{badge}</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 再来一次按钮，重置游戏
    if st.button("🔄 再来一次", type="primary", use_container_width=True):
        reset_game()

else:
    # ---- 当前关卡内容 ----
    # 获取当前关卡数据
    level = st.session_state.levels[current_idx]

    # 使用卡片样式包装关卡内容（带边框）
    with st.container(border=True):
        # 关卡标题
        st.subheader(f"### {level['title']}")

        # 问题描述（支持 Markdown 和代码块）
        st.markdown("**问题:**")
        st.markdown(level["question"])

        # 选项列表
        st.markdown("**请选择答案:**")

        # 获取当前选中的选项索引
        # 如果之前已选择过选项，保持选择状态
        if st.session_state.selected_option in level["options"]:
            default_index = level["options"].index(st.session_state.selected_option)
        else:
            default_index = 0

        # 单选按钮组
        # disabled 参数：当显示答案结果时禁用选择，防止用户修改答案
        selected = st.radio(
            label="选项",
            options=level["options"],
            index=default_index,
            label_visibility="collapsed",  # 隐藏标签
            disabled=st.session_state.show_result  # 答案展示时禁用选择
        )
        
        # 保存选中的选项到 session_state
        # 这样在页面刷新后能保持用户的选择
        st.session_state.selected_option = selected

        # ============================================================
        # 根据 show_result 状态显示不同内容
        # ============================================================
        if st.session_state.show_result:
            # ---- 答案展示环节 ----
            # 用户提交答案后，进入此环节显示答案解析
            
            st.markdown("---")
            st.markdown("### 📝 答案解析")
            
            # 根据答题结果显示不同提示
            if st.session_state.is_correct:
                # 答对的情况
                st.success("🎊 回答正确!", icon="✅")
                st.markdown(f"**正确答案:** {level['answer']}")
                # 如果获得了新徽章，显示获得提示
                if st.session_state.earned_reward:
                    st.info(f"恭喜获得徽章: {st.session_state.earned_reward}")
            else:
                # 答错的情况
                st.error("😢 回答错误!", icon="🚫")
                st.markdown(f"**你的答案:** {st.session_state.selected_option}")
                st.markdown(f"**正确答案:** {level['answer']}")
                # 如果是第二次答错，提示不得分
                if st.session_state.wrong_attempts >= 2:
                    st.warning("此题已用完尝试次数，不得分")
            
            # 进入下一关按钮
            # 用户需要手动点击才能进入下一关
            if st.button("➡️ 进入下一关", type="primary", use_container_width=True):
                # 清空当前关卡的状态
                st.session_state.selected_option = None
                st.session_state.wrong_attempts = 0
                st.session_state.show_result = False
                # 进入下一关（索引 +1）
                st.session_state.current_level += 1
                # 刷新页面
                st.rerun()
        else:
            # ---- 答题环节 ----
            # 用户正在答题
            
            # 显示剩余尝试次数
            remaining_attempts = 2 - st.session_state.wrong_attempts
            st.markdown(f"**剩余尝试次数:** {remaining_attempts} 次")

            # 提交答案按钮
            st.markdown("")
            if st.button("提交答案", type="primary", use_container_width=True):
                # 判断答案是否正确
                if selected == level["answer"]:
                    # ---- 答对的情况 ----
                    # 记录答题正确
                    st.session_state.is_correct = True
                    st.session_state.earned_reward = None

                    # 根据错误次数决定得分
                    # 一次答对（wrong_attempts = 0）：10分
                    # 错了一次才答对（wrong_attempts = 1）：5分
                    if st.session_state.wrong_attempts == 0:
                        points_earned = 10
                    else:
                        points_earned = 5
                    st.session_state.score += points_earned

                    # 获得徽章
                    reward = level["reward"]
                    # 检查是否已获得该徽章，避免重复获得
                    if reward not in st.session_state.badges:
                        st.session_state.badges.append(reward)
                        st.session_state.earned_reward = reward

                    # 进入答案展示环节
                    st.session_state.show_result = True
                    st.rerun()
                else:
                    # ---- 答错的情况 ----
                    # 记录答题错误
                    st.session_state.is_correct = False
                    st.session_state.wrong_attempts += 1
                    
                    if st.session_state.wrong_attempts >= 2:
                        # 第二次答错
                        # 进入答案展示环节，显示正确答案
                        st.session_state.show_result = True
                        st.rerun()
                    else:
                        # 第一次答错
                        # 不显示正确答案，允许再试一次
                        st.error("回答错误，请重新选择答案!", icon="🚫")
                        st.warning("提示: 仔细想想，再试一次 😊")