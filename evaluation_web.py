# 保存为：evaluation_web.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# 页面全局配置（手机端优先适配）
st.set_page_config(
    page_title="中小学职称评审综合测评系统",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===================== 系统核心配置 =====================
ADMIN_PASSWORD = "admin123456"
EVALUATED_PERSONS = [f"被测评人{i}" for i in range(1, 41)]
EVALUATOR_ROLES = ["领导", "老师", "家长", "学生"]
MORAL_DIMENSIONS = [
    "坚定政治方向", "自觉爱国守法", "传播优秀文化", "潜心教书育人", "关心爱护学生",
    "加强安全防范", "坚持言行雅正", "秉持公平诚信", "坚守廉洁自律", "规范从教行为"
]
TEACHING_DIMENSIONS = ["教学态度", "教学能力", "教学效果"]
DATA_FILE = "evaluation_data.json"

# ===================== 工具函数 =====================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(record):
    data = load_data()
    data.append(record)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_grade(score):
    if score <= 0:
        return "未评分"
    elif 80 <= score <= 95:
        return "优秀 🟢"
    elif 70 <= score <= 79:
        return "良好 🔵"
    elif 60 <= score <= 69:
        return "一般 🟠"
    elif 0 < score <= 59:
        return "不合格 🔴"
    else:
        return "分值无效 ⚫"

def admin_auth(password):
    return password == ADMIN_PASSWORD

def calculate_scores():
    """仅计算得分，不修改任何session_state"""
    moral_scores = []
    for dim in MORAL_DIMENSIONS:
        score = st.session_state.get(f"score_{dim}", 0.0)
        if score > 0:
            moral_scores.append(score)

    teaching_scores = []
    for dim in TEACHING_DIMENSIONS:
        score = st.session_state.get(f"score_{dim}", 0.0)
        if score > 0:
            teaching_scores.append(score)

    moral_avg = round(np.mean(moral_scores), 1) if len(moral_scores) == len(MORAL_DIMENSIONS) else None
    teaching_avg = round(np.mean(teaching_scores), 1) if len(teaching_scores) == len(TEACHING_DIMENSIONS) else None
    final_score = round((moral_avg * 0.5) + (teaching_avg * 0.5), 1) if (moral_avg and teaching_avg) else None
    
    return moral_avg, teaching_avg, final_score

# ===================== 初始化：仅在首次加载时初始化，永不修改 =====================
# 管理员状态
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 评分维度：仅初始化一次，后续永不修改（核心！）
for dim in MORAL_DIMENSIONS + TEACHING_DIMENSIONS:
    key = f"score_{dim}"
    if key not in st.session_state:
        st.session_state[key] = 0.0

# ===================== 侧边栏管理员入口 =====================
with st.sidebar:
    st.markdown("### 🔐 管理员后台")
    if not st.session_state.is_admin:
        admin_pwd = st.text_input("请输入管理员密码", type="password", placeholder="输入密码后登录")
        if st.button("登录", use_container_width=True, type="primary"):
            if admin_auth(admin_pwd):
                st.session_state.is_admin = True
                st.success("✅ 管理员登录成功！")
                st.rerun()
            else:
                st.error("❌ 密码错误，请重新输入！")
    else:
        st.success("✅ 当前为管理员模式")
        if st.button("退出管理员", use_container_width=True, type="secondary"):
            st.session_state.is_admin = False
            st.rerun()

# ===================== 普通用户界面 =====================
st.title("📝 中小学职称评审综合测评")
st.markdown("### 手机端专用 | 自定义分值提交")
st.markdown("---")
st.markdown("#### ⚠️ 评分标准：优秀(80-95) | 良好(70-79) | 一般(60-69) | 不合格(1-59)")
st.markdown("#### 📌 提示：分值填0代表未填写，请输入1-100的有效分值")
st.markdown("---")

# 1. 基础信息选择
col1, col2 = st.columns(2)
with col1:
    selected_person = st.selectbox("🔍 选择被测评人", EVALUATED_PERSONS, key="person", placeholder="请选择")
with col2:
    evaluator_role = st.selectbox("👤 你的测评身份", EVALUATOR_ROLES, key="role", placeholder="请选择")

st.markdown("---")

# 2. 师德表现评分（仅读取，不修改session_state）
st.markdown("### 🎯 师德表现评价（权重50%）")
moral_col1, moral_col2 = st.columns(2)
for idx, dim in enumerate(MORAL_DIMENSIONS):
    with moral_col1 if idx % 2 == 0 else moral_col2:
        # 仅渲染输入框，永不修改对应的session_state
        score = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入1-100分值",
            label_visibility="visible"
        )
        st.caption(f"等级：{get_grade(score)}")

st.markdown("---")

# 3. 教学业绩评分（仅读取，不修改session_state）
st.markdown("### 📚 教学业绩评价（权重50%）")
teaching_col1, teaching_col2, teaching_col3 = st.columns(3)
for idx, dim in enumerate(TEACHING_DIMENSIONS):
    with [teaching_col1, teaching_col2, teaching_col3][idx]:
        score = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入1-100分值",
            label_visibility="visible"
        )
        st.caption(f"等级：{get_grade(score)}")

# 4. 实时计算得分（仅返回结果，不修改session_state）
moral_avg, teaching_avg, final_score = calculate_scores()

st.markdown("---")

# 5. 结果展示
st.markdown("### 📊 你的测评结果")
if final_score is not None:
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric("师德表现平均分", f"{moral_avg} 分", get_grade(moral_avg))
    with res_col2:
        st.metric("教学业绩平均分", f"{teaching_avg} 分", get_grade(teaching_avg))
    with res_col3:
        st.metric("最终综合得分", f"{final_score} 分", get_grade(final_score))
else:
    st.warning("⚠️ 请补全所有维度的有效分值（1-100），填完后将自动显示测评结果！")

st.markdown("---")

# 6. 提交按钮（核心：提交后不修改session_state，仅保存数据+跳转）
submit_btn = st.button(
    "💾 提交测评结果",
    use_container_width=True,
    type="primary",
    disabled=final_score is None
)

if submit_btn:
    # 1. 构建并保存记录（仅读取session_state，不修改）
    moral_details = {dim: st.session_state[f"score_{dim}"] for dim in MORAL_DIMENSIONS}
    teaching_details = {dim: st.session_state[f"score_{dim}"] for dim in TEACHING_DIMENSIONS}
    
    submit_record = {
        "测评时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "被测评人": selected_person,
        "测评人身份": evaluator_role,
        "师德表现各维度得分": moral_details,
        "教学业绩各维度得分": teaching_details,
        "师德表现平均分": moral_avg,
        "教学业绩平均分": teaching_avg,
        "最终综合得分": final_score
    }
    save_data(submit_record)
    
    # 2. 跳转实现重置（核心：不修改session_state，用URL参数提示成功）
    st.query_params["submitted"] = "success"
    st.rerun(0.0)  # 刷新页面，所有输入框回到初始值（首次初始化的0.0）
    
# ===================== 提交成功提示（用URL参数实现，无session_state修改）=====================
query_params = st.query_params
if "submitted" in query_params and query_params["submitted"] == "success":
    st.success(f"""✅ 测评结果提交成功！
    提交时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    已自动重置为初始状态，可继续测评~
    """)
    # 清除URL参数，避免刷新后重复显示
    st.query_params.clear()

# 手机端提示
st.markdown("---")
st.caption("💡 手机操作小贴士：所有分值填完自动出结果，确认无误后点击提交即可，提交后自动重置可继续测评~")

# ===================== 管理员功能区 =====================
if st.session_state.is_admin:
    st.markdown("---")
    st.markdown("## 🛡️ 管理员专属 | 测评数据统计与导出")
    st.markdown("### 统计维度：按被测评人分组 + 按测评人身份细分")
    st.markdown("---")
    
    all_data = load_data()
    if not all_data:
        st.info("📭 暂无测评数据，请等待用户提交后再查看统计！")
    else:
        df_raw = pd.DataFrame(all_data)
        df_stats = df_raw[["测评时间", "被测评人", "测评人身份", "师德表现平均分", "教学业绩平均分", "最终综合得分"]].copy()
        
        # 1. 全量概览
        st.markdown("### 📈 全量测评数据概览")
        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
        with overview_col1:
            st.metric("总提交记录数", len(df_stats))
        with overview_col2:
            st.metric("参与被测评人数", df_stats["被测评人"].nunique())
        with overview_col3:
            st.metric("整体平均最终得分", f"{df_stats['最终综合得分'].mean():.1f} 分")
        with overview_col4:
            st.metric("测评身份类型数", df_stats["测评人身份"].nunique())
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
        
        # 2. 双维度核心统计
        st.markdown("### 🔍 核心统计：被测评人 × 测评人身份 双维度")
        double_group = df_stats.groupby(["被测评人", "测评人身份"]).agg({
            "最终综合得分": ["count", "mean", "max", "min"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        double_group.columns = ["测评次数", "平均最终得分", "最高得分", "最低得分", "平均师德得分", "平均教学得分"]
        double_group = double_group.reset_index()
        st.dataframe(double_group, use_container_width=True)
        
        # 3. 按被测评人汇总
        st.markdown("### 📋 按被测评人汇总统计")
        person_group = df_stats.groupby("被测评人").agg({
            "最终综合得分": ["count", "mean", "max", "min", "std"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        person_group.columns = ["总测评次数", "平均最终得分", "最高得分", "最低得分", "得分标准差", "平均师德得分", "平均教学得分"]
        st.dataframe(person_group, use_container_width=True)
        
        # 4. 按身份汇总
        st.markdown("### 📋 按测评人身份汇总统计")
        role_group = df_stats.groupby("测评人身份").agg({
            "最终综合得分": ["count", "mean", "std"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        role_group.columns = ["测评总次数", "平均最终得分", "得分标准差", "平均师德得分", "平均教学得分"]
        st.dataframe(role_group, use_container_width=True)
        
        # 5. 数据导出
        st.markdown("### 📥 全量数据导出")
        csv_data = df_raw.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下载所有测评数据（CSV/Excel兼容）",
            data=csv_data,
            file_name=f"中小学职称测评全量数据_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
