# 保存为：evaluation_web.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# 页面配置
st.set_page_config(
    page_title="中小学职称评审综合测评系统（手机版）",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 基础数据配置
EVALUATED_PERSONS = [f"被测评人{i}" for i in range(1, 41)]  # 40人名单
EVALUATOR_ROLES = ["领导", "老师", "家长", "学生"]
MORAL_DIMENSIONS = [
    "坚定政治方向", "自觉爱国守法", "传播优秀文化", "潜心教书育人", "关心爱护学生",
    "加强安全防范", "坚持言行雅正", "秉持公平诚信", "坚守廉洁自律", "规范从教行为"
]
TEACHING_DIMENSIONS = ["教学态度", "教学能力", "教学效果"]
SCORE_RANGES = {
    "优秀": (80, 95), "良好": (70, 79), "一般": (60, 69), "不合格": (0, 59)
}

# 数据存储路径
DATA_FILE = "evaluation_data.json"

# 初始化会话状态
if "moral_scores" not in st.session_state:
    st.session_state.moral_scores = {dim: 85.0 for dim in MORAL_DIMENSIONS}
if "teaching_scores" not in st.session_state:
    st.session_state.teaching_scores = {dim: 85.0 for dim in TEACHING_DIMENSIONS}
if "final_score" not in st.session_state:
    st.session_state.final_score = None
if "moral_avg" not in st.session_state:
    st.session_state.moral_avg = None
if "teaching_avg" not in st.session_state:
    st.session_state.teaching_avg = None

# 工具函数
def load_data():
    """加载历史测评数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(record):
    """保存测评记录"""
    data = load_data()
    data.append(record)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_grade(score):
    """根据分数判断等级"""
    if 80 <= score <= 95:
        return "优秀 🟢"
    elif 70 <= score <= 79:
        return "良好 🔵"
    elif 60 <= score <= 69:
        return "一般 🟠"
    elif 0 <= score <= 59:
        return "不合格 🔴"
    else:
        return "超出范围 ⚫"

# 页面标题（适配手机显示）
st.title("📝 中小学职称评审综合测评系统")
st.markdown("### 手机端专用版 | 支持自定义分值输入")
st.markdown("---")

# 第一步：选择被测评人和测评人身份（手机适配的布局）
col1, col2 = st.columns(2)
with col1:
    selected_person = st.selectbox("🔍 选择被测评人", EVALUATED_PERSONS, key="person")
with col2:
    evaluator_role = st.selectbox("👤 你的测评身份", EVALUATOR_ROLES, key="role")

# 评分说明（醒目提示）
st.markdown("### ⚠️ 评分标准：优秀(80-95) | 良好(70-79) | 一般(60-69) | 不合格(≤59)")

# 第二步：师德表现评分（手机适配的滚动布局）
st.markdown("### 🎯 师德表现评价（权重50%）")
moral_col1, moral_col2 = st.columns(2)
for i, dim in enumerate(MORAL_DIMENSIONS):
    with moral_col1 if i % 2 == 0 else moral_col2:
        score = st.number_input(
            f"{dim}",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.moral_scores[dim],
            step=0.5,
            key=f"moral_{dim}"
        )
        st.session_state.moral_scores[dim] = score
        st.caption(f"当前等级：{get_grade(score)}")

# 第三步：教学业绩评分
st.markdown("### 📚 教学业绩评价（权重50%）")
teaching_cols = st.columns(3)
for i, dim in enumerate(TEACHING_DIMENSIONS):
    with teaching_cols[i]:
        score = st.number_input(
            f"{dim}",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.teaching_scores[dim],
            step=0.5,
            key=f"teaching_{dim}"
        )
        st.session_state.teaching_scores[dim] = score
        st.caption(f"当前等级：{get_grade(score)}")

# 第四步：计算得分按钮
st.markdown("---")
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🧮 计算最终得分", type="primary", use_container_width=True):
        # 计算平均分
        moral_scores_list = list(st.session_state.moral_scores.values())
        teaching_scores_list = list(st.session_state.teaching_scores.values())
        st.session_state.moral_avg = np.mean(moral_scores_list)
        st.session_state.teaching_avg = np.mean(teaching_scores_list)
        # 计算最终得分（50%+50%）
        st.session_state.final_score = (st.session_state.moral_avg * 0.5) + (st.session_state.teaching_avg * 0.5)

# 显示计算结果
if st.session_state.final_score is not None:
    st.markdown("### 📊 测评结果")
    result_col1, result_col2, result_col3 = st.columns(3)
    with result_col1:
        st.metric("师德表现平均分", f"{st.session_state.moral_avg:.1f} 分", get_grade(st.session_state.moral_avg))
    with result_col2:
        st.metric("教学业绩平均分", f"{st.session_state.teaching_avg:.1f} 分", get_grade(st.session_state.teaching_avg))
    with result_col3:
        st.metric("最终综合得分", f"{st.session_state.final_score:.1f} 分", get_grade(st.session_state.final_score), delta_color="normal")

# 第五步：保存测评结果
with col_btn2:
    if st.button("💾 保存测评结果", use_container_width=True, disabled=st.session_state.final_score is None):
        # 构建测评记录
        record = {
            "测评时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "被测评人": selected_person,
            "测评人身份": evaluator_role,
            "师德表现得分": st.session_state.moral_scores,
            "教学业绩得分": st.session_state.teaching_scores,
            "师德平均分": float(st.session_state.moral_avg),
            "教学平均分": float(st.session_state.teaching_avg),
            "最终综合得分": float(st.session_state.final_score)
        }
        # 保存数据
        save_data(record)
        st.success(f"✅ 测评结果已保存！\n被测评人：{selected_person}\n最终得分：{st.session_state.final_score:.1f}分")

# 第六步：查看/导出历史数据
st.markdown("---")
with st.expander("📋 查看/导出历史测评数据", expanded=False):
    data = load_data()
    if data:
        # 转换为DataFrame方便显示
        df_data = []
        for rec in data:
            df_data.append({
                "测评时间": rec["测评时间"],
                "被测评人": rec["被测评人"],
                "测评人身份": rec["测评人身份"],
                "师德平均分": rec["师德平均分"],
                "教学平均分": rec["教学平均分"],
                "最终得分": rec["最终综合得分"]
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # 导出Excel
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 导出为Excel/CSV文件",
            data=csv_data,
            file_name=f"职称测评数据_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # 统计汇总
        st.markdown("### 📈 统计汇总")
        summary = df.groupby("被测评人").agg({
            "最终得分": ["count", "mean", "max", "min"],
            "师德平均分": "mean",
            "教学平均分": "mean"
        }).round(1)
        summary.columns = ["测评次数", "平均最终得分", "最高得分", "最低得分", "平均师德得分", "平均教学得分"]
        st.dataframe(summary, use_container_width=True)
    else:
        st.info("暂无历史测评数据，请先完成测评并保存")

# 重置按钮
if st.button("🔄 清空当前评分", type="secondary", use_container_width=True):
    st.session_state.moral_scores = {dim: 85.0 for dim in MORAL_DIMENSIONS}
    st.session_state.teaching_scores = {dim: 85.0 for dim in TEACHING_DIMENSIONS}
    st.session_state.final_score = None
    st.session_state.moral_avg = None
    st.session_state.teaching_avg = None
    st.rerun()

# 手机适配的底部提示
st.markdown("---")
st.caption("💡 手机端操作提示：可左右滑动查看全部选项，输入分数后点击计算即可")
