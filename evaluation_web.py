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
    layout="centered",  # 手机端居中布局更友好
    initial_sidebar_state="collapsed"
)

# ===================== 系统核心配置（可自定义修改）=====================
# 管理员密码（务必修改为自己的复杂密码）
ADMIN_PASSWORD = "admin123456"
# 40名被测评人名单
EVALUATED_PERSONS = [f"被测评人{i}" for i in range(1, 41)]
# 测评人身份选项
EVALUATOR_ROLES = ["领导", "老师", "家长", "学生"]
# 师德表现10个维度（权重50%）
MORAL_DIMENSIONS = [
    "坚定政治方向", "自觉爱国守法", "传播优秀文化", "潜心教书育人", "关心爱护学生",
    "加强安全防范", "坚持言行雅正", "秉持公平诚信", "坚守廉洁自律", "规范从教行为"
]
# 教学业绩3个维度（权重50%）
TEACHING_DIMENSIONS = ["教学态度", "教学能力", "教学效果"]
# 评分等级标准
SCORE_RANGES = {
    "优秀": (80, 95), "良好": (70, 79), "一般": (60, 69), "不合格": (0, 59)
}
# 测评数据存储文件
DATA_FILE = "evaluation_data.json"

# ===================== 会话状态初始化（页面刷新不丢失）=====================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False  # 默认非管理员
if "final_score" not in st.session_state:
    st.session_state.final_score = None  # 最终得分
if "moral_avg" not in st.session_state:
    st.session_state.moral_avg = None    # 师德平均分
if "teaching_avg" not in st.session_state:
    st.session_state.teaching_avg = None# 教学平均分
# 初始化所有评分维度为空（无默认值85）
for dim in MORAL_DIMENSIONS + TEACHING_DIMENSIONS:
    if f"score_{dim}" not in st.session_state:
        st.session_state[f"score_{dim}"] = None

# ===================== 工具函数（核心逻辑，无需修改）=====================
def load_data():
    """加载所有测评提交数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return []
    return []

def save_data(record):
    """保存用户提交的测评记录"""
    data = load_data()
    data.append(record)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_grade(score):
    """根据分数自动判断等级"""
    if score is None:
        return "未评分"
    if 80 <= score <= 95:
        return "优秀 🟢"
    elif 70 <= score <= 79:
        return "良好 🔵"
    elif 60 <= score <= 69:
        return "一般 🟠"
    elif 0 <= score <= 59:
        return "不合格 🔴"
    else:
        return "分值无效 ⚫"

def admin_auth(password):
    """管理员密码验证"""
    return password == ADMIN_PASSWORD

def auto_calculate_scores():
    """自动计算所有得分：实时监测输入，无计算按钮"""
    # 收集师德表现分数（过滤空值）
    moral_scores = [st.session_state[f"score_{dim}"] for dim in MORAL_DIMENSIONS]
    if None in moral_scores:
        st.session_state.moral_avg = None
    else:
        st.session_state.moral_avg = round(np.mean(moral_scores), 1)
    
    # 收集教学业绩分数（过滤空值）
    teaching_scores = [st.session_state[f"score_{dim}"] for dim in TEACHING_DIMENSIONS]
    if None in teaching_scores:
        st.session_state.teaching_avg = None
    else:
        st.session_state.teaching_avg = round(np.mean(teaching_scores), 1)
    
    # 计算最终综合得分（师德50% + 教学50%）
    if st.session_state.moral_avg is not None and st.session_state.teaching_avg is not None:
        st.session_state.final_score = round(
            (st.session_state.moral_avg * 0.5) + (st.session_state.teaching_avg * 0.5), 1
        )
    else:
        st.session_state.final_score = None

# ===================== 侧边栏：管理员专属登录入口=====================
with st.sidebar:
    st.markdown("### 🔐 管理员后台")
    if not st.session_state.is_admin:
        # 非管理员：仅显示密码输入框
        admin_pwd = st.text_input("请输入管理员密码", type="password", placeholder="输入密码后登录")
        if st.button("登录", use_container_width=True, type="primary"):
            if admin_auth(admin_pwd):
                st.session_state.is_admin = True
                st.success("✅ 管理员登录成功！")
                st.rerun()
            else:
                st.error("❌ 密码错误，请重新输入！")
    else:
        # 管理员：显示登录状态+退出按钮
        st.success("✅ 当前为管理员模式")
        st.info("📊 下方可查看/统计所有测评数据")
        if st.button("退出管理员", use_container_width=True, type="secondary"):
            st.session_state.is_admin = False
            st.info("已退出管理员模式")
            st.rerun()

# ===================== 普通用户核心界面（所有人可见，极简设计）=====================
st.title("📝 中小学职称评审综合测评")
st.markdown("### 手机端专用 | 自定义分值提交")
st.markdown("---")
st.markdown("#### ⚠️ 评分标准：优秀(80-95) | 良好(70-79) | 一般(60-69) | 不合格(≤59)")
st.markdown("---")

# 第一步：基础信息选择（被测评人+测评人身份）
col1, col2 = st.columns(2)
with col1:
    selected_person = st.selectbox("🔍 选择被测评人", EVALUATED_PERSONS, key="person", placeholder="请选择")
with col2:
    evaluator_role = st.selectbox("👤 你的测评身份", EVALUATOR_ROLES, key="role", placeholder="请选择")

st.markdown("---")

# 第二步：师德表现评分（10维度，默认空，输入后实时计算）
st.markdown("### 🎯 师德表现评价（权重50%）")
moral_col1, moral_col2 = st.columns(2)
for idx, dim in enumerate(MORAL_DIMENSIONS):
    with moral_col1 if idx % 2 == 0 else moral_col2:
        # 分值默认空，仅接受0-100的数字，步长0.5
        score = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入0-100分值",
            label_visibility="visible"
        )
        # 实时更新会话状态（为空时设为None，避免0值干扰）
        st.session_state[f"score_{dim}"] = score if score != 0.0 or st.session_state[f"score_{dim}"] == 0.0 else None
        # 显示当前评分等级
        st.caption(f"等级：{get_grade(st.session_state[f'score_{dim}'])}")

st.markdown("---")

# 第三步：教学业绩评分（3维度，默认空，输入后实时计算）
st.markdown("### 📚 教学业绩评价（权重50%）")
teaching_col1, teaching_col2, teaching_col3 = st.columns(3)
for idx, dim in enumerate(TEACHING_DIMENSIONS):
    with [teaching_col1, teaching_col2, teaching_col3][idx]:
        # 分值默认空，仅接受0-100的数字，步长0.5
        score = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入0-100分值",
            label_visibility="visible"
        )
        # 实时更新会话状态
        st.session_state[f"score_{dim}"] = score if score != 0.0 or st.session_state[f"score_{dim}"] == 0.0 else None
        # 显示当前评分等级
        st.caption(f"等级：{get_grade(st.session_state[f'score_{dim}'])}")

# 实时自动计算得分（无按钮，输入完成即刻出结果）
auto_calculate_scores()

st.markdown("---")

# 第四步：测评结果展示（所有分值填完后自动显示）
st.markdown("### 📊 你的测评结果")
if st.session_state.final_score is not None:
    # 所有分值填完：显示完整得分
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric("师德表现平均分", f"{st.session_state.moral_avg} 分", get_grade(st.session_state.moral_avg))
    with res_col2:
        st.metric("教学业绩平均分", f"{st.session_state.teaching_avg} 分", get_grade(st.session_state.teaching_avg))
    with res_col3:
        st.metric("最终综合得分", f"{st.session_state.final_score} 分", get_grade(st.session_state.final_score))
else:
    # 有未填分值：提示补全
    st.warning("⚠️ 请补全所有维度的分值，填完后将自动显示测评结果！")

st.markdown("---")

# 第五步：唯一提交按钮（所有分值填完后才可点击，提交后自动清空）
submit_btn = st.button(
    "💾 提交测评结果",
    use_container_width=True,
    type="primary",
    disabled=st.session_state.final_score is None  # 结果为空时禁用按钮
)

if submit_btn:
    # 构建测评提交记录
    submit_record = {
        "测评时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "被测评人": selected_person,
        "测评人身份": evaluator_role,
        "师德表现各维度得分": {dim: st.session_state[f"score_{dim}"] for dim in MORAL_DIMENSIONS},
        "教学业绩各维度得分": {dim: st.session_state[f"score_{dim}"] for dim in TEACHING_DIMENSIONS},
        "师德表现平均分": st.session_state.moral_avg,
        "教学业绩平均分": st.session_state.teaching_avg,
        "最终综合得分": st.session_state.final_score
    }
    # 保存记录
    save_data(submit_record)
    st.success(f"""✅ 测评结果提交成功！
    被测评人：{selected_person}
    最终综合得分：{st.session_state.final_score} 分
    提交时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    # 提交后自动清空所有分值和结果（准备下一次测评）
    st.session_state.final_score = None
    st.session_state.moral_avg = None
    st.session_state.teaching_avg = None
    for dim in MORAL_DIMENSIONS + TEACHING_DIMENSIONS:
        st.session_state[f"score_{dim}"] = None
    # 页面刷新，回到初始状态
    st.rerun()

# 手机端操作提示
st.markdown("---")
st.caption("💡 手机操作小贴士：所有分值填完自动出结果，确认无误后点击提交即可，提交后自动清空可继续测评~")

# ===================== 管理员专属功能区（仅登录后可见，按被测评人+身份双维度统计）=====================
if st.session_state.is_admin:
    st.markdown("---")
    st.markdown("## 🛡️ 管理员专属 | 测评数据统计与导出")
    st.markdown("### 统计维度：按被测评人分组 + 按测评人身份细分")
    st.markdown("---")
    
    # 加载所有测评数据
    all_data = load_data()
    if not all_data:
        st.info("📭 暂无测评数据，请等待用户提交后再查看统计！")
    else:
        # 转换为DataFrame，方便统计分析
        df_raw = pd.DataFrame(all_data)
        # 提取核心统计字段
        df_stats = df_raw[["测评时间", "被测评人", "测评人身份", "师德表现平均分", "教学业绩平均分", "最终综合得分"]].copy()
        
        # 1. 全量数据概览
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
        
        # 2. 核心统计：按【被测评人】分组 + 【测评人身份】细分（核心需求）
        st.markdown("### 🔍 核心统计：被测评人 × 测评人身份 双维度")
        # 按被测评人+测评人身份双重分组统计
        double_group = df_stats.groupby(["被测评人", "测评人身份"]).agg({
            "最终综合得分": ["count", "mean", "max", "min"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        # 重命名列，更易读
        double_group.columns = ["测评次数", "平均最终得分", "最高得分", "最低得分", "平均师德得分", "平均教学得分"]
        double_group = double_group.reset_index()  # 取消索引，显示被测评人+身份列
        st.dataframe(double_group, use_container_width=True)
        
        # 3. 按被测评人汇总（合并所有身份的统计）
        st.markdown("### 📋 按被测评人汇总统计（所有身份合并）")
        person_group = df_stats.groupby("被测评人").agg({
            "最终综合得分": ["count", "mean", "max", "min", "std"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        person_group.columns = ["总测评次数", "平均最终得分", "最高得分", "最低得分", "得分标准差", "平均师德得分", "平均教学得分"]
        st.dataframe(person_group, use_container_width=True)
        
        # 4. 按测评人身份汇总统计
        st.markdown("### 📋 按测评人身份汇总统计（所有被测评人合并）")
        role_group = df_stats.groupby("测评人身份").agg({
            "最终综合得分": ["count", "mean", "std"],
            "师德表现平均分": "mean",
            "教学业绩平均分": "mean"
        }).round(1)
        role_group.columns = ["测评总次数", "平均最终得分", "得分标准差", "平均师德得分", "平均教学得分"]
        st.dataframe(role_group, use_container_width=True)
        
        # 5. 全量数据导出（CSV格式，可直接用Excel打开）
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
