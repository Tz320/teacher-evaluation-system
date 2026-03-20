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
# 权重配置（核心：明确师德50%、教学50%）
MORAL_WEIGHT = 0.5
TEACHING_WEIGHT = 0.5
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
    """等级判断逻辑"""
    if score is None or score <= 0:
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

# ===================== 初始化会话状态（核心：存储输入值，触发实时重运行）=====================
# 管理员状态
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
# 提交成功状态
if "submission_success" not in st.session_state:
    st.session_state.submission_success = False
if "submission_info" not in st.session_state:
    st.session_state.submission_info = {}
# 存储所有评分维度的输入值（关键：用session_state触发实时重运行）
for dim in MORAL_DIMENSIONS + TEACHING_DIMENSIONS:
    key = f"score_{dim}"
    if key not in st.session_state:
        st.session_state[key] = 0.0  # 初始值0.0，代表未填写

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

# ===================== 普通用户界面（核心：放弃表单，用session_state实现实时计算）=====================
st.title("📝 中小学职称评审综合测评")
st.markdown("### 手机端专用 | 输入即计算，实时显示结果")
st.markdown("---")
st.markdown("#### ⚠️ 评分标准：优秀(80-95) | 良好(70-79) | 一般(60-69) | 不合格(1-59)")
st.markdown(f"#### ⚖️ 权重配置：师德表现({MORAL_WEIGHT*100}%) + 教学业绩({TEACHING_WEIGHT*100}%)")
st.markdown("---")

# 1. 基础信息选择（强制用户选择，不能为空）
col1, col2 = st.columns(2)
with col1:
    st.session_state["selected_person"] = st.selectbox(
        "🔍 选择被测评人", 
        [""] + EVALUATED_PERSONS,  # 空选项强制选择
        key="selected_person"
    )
with col2:
    st.session_state["evaluator_role"] = st.selectbox(
        "👤 你的测评身份", 
        [""] + EVALUATOR_ROLES,  # 空选项强制选择
        key="evaluator_role"
    )

st.markdown("---")

# 2. 师德表现评分（核心：每个输入框绑定session_state，输入即触发重运行）
st.markdown("### 🎯 师德表现评价（权重50%）")
moral_col1, moral_col2 = st.columns(2)
for idx, dim in enumerate(MORAL_DIMENSIONS):
    with moral_col1 if idx % 2 == 0 else moral_col2:
        # 关键：输入框直接绑定session_state，输入值实时同步
        st.session_state[f"score_{dim}"] = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入1-100分值",
            label_visibility="visible",
            value=st.session_state[f"score_{dim}"]  # 保持输入状态
        )
        # 实时显示等级
        current_score = st.session_state[f"score_{dim}"]
        st.caption(f"等级：{get_grade(current_score)} | 分值：{current_score if current_score > 0 else '未填写'}")

st.markdown("---")

# 3. 教学业绩评分（同上，绑定session_state实现实时响应）
st.markdown("### 📚 教学业绩评价（权重50%）")
teaching_col1, teaching_col2, teaching_col3 = st.columns(3)
for idx, dim in enumerate(TEACHING_DIMENSIONS):
    with [teaching_col1, teaching_col2, teaching_col3][idx]:
        st.session_state[f"score_{dim}"] = st.number_input(
            dim,
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key=f"score_{dim}",
            placeholder="输入1-100分值",
            label_visibility="visible",
            value=st.session_state[f"score_{dim}"]
        )
        current_score = st.session_state[f"score_{dim}"]
        st.caption(f"等级：{get_grade(current_score)} | 分值：{current_score if current_score > 0 else '未填写'}")

st.markdown("---")

# 4. 实时计算得分（核心：输入值变化即触发计算，权重生效）
def calculate_real_time():
    """实时计算得分，明确权重逻辑"""
    # 收集师德有效分值（>0）
    moral_scores = []
    for dim in MORAL_DIMENSIONS:
        score = st.session_state[f"score_{dim}"]
        if score > 0:
            moral_scores.append(score)
    
    # 收集教学有效分值（>0）
    teaching_scores = []
    for dim in TEACHING_DIMENSIONS:
        score = st.session_state[f"score_{dim}"]
        if score > 0:
            teaching_scores.append(score)
    
    # 计算条件：所有维度都填写有效分值
    all_moral_filled = len(moral_scores) == len(MORAL_DIMENSIONS)
    all_teaching_filled = len(teaching_scores) == len(TEACHING_DIMENSIONS)
    base_info_filled = st.session_state["selected_person"] != "" and st.session_state["evaluator_role"] != ""
    
    if all_moral_filled and all_teaching_filled and base_info_filled:
        # 计算平均分
        moral_avg = round(np.mean(moral_scores), 1)
        teaching_avg = round(np.mean(teaching_scores), 1)
        # 权重计算（核心：师德50% + 教学50%）
        final_score = round(
            (moral_avg * MORAL_WEIGHT) + (teaching_avg * TEACHING_WEIGHT),
            1
        )
        return moral_avg, teaching_avg, final_score, True
    else:
        # 未填完时，返回未填信息
        unfilled = []
        if not base_info_filled:
            unfilled.append("被测评人/测评身份未选择")
        if not all_moral_filled:
            unfilled.append(f"师德表现还有{len(MORAL_DIMENSIONS)-len(moral_scores)}个维度未填写")
        if not all_teaching_filled:
            unfilled.append(f"教学业绩还有{len(TEACHING_DIMENSIONS)-len(teaching_scores)}个维度未填写")
        return None, None, None, False, " | ".join(unfilled)

# 执行实时计算
moral_avg, teaching_avg, final_score, is_ready, unfilled_info = calculate_real_time()

# 5. 显示计算结果（实时更新）
st.markdown("### 📊 实时测评结果")
if is_ready:
    # 所有信息填完，显示完整结果（含权重说明）
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric(
            f"师德表现平均分（{MORAL_WEIGHT*100}%）", 
            f"{moral_avg} 分", 
            get_grade(moral_avg)
        )
    with res_col2:
        st.metric(
            f"教学业绩平均分（{TEACHING_WEIGHT*100}%）", 
            f"{teaching_avg} 分", 
            get_grade(teaching_avg)
        )
    with res_col3:
        st.metric(
            "最终综合得分", 
            f"{final_score} 分", 
            get_grade(final_score),
            delta=f"师德×{MORAL_WEIGHT}+教学×{TEACHING_WEIGHT}",
            delta_color="normal"
        )
else:
    # 未填完，显示未填信息
    st.warning(f"⚠️ 暂无法计算得分：{unfilled_info}")

st.markdown("---")

# 6. 提交按钮（仅当所有信息填完才启用）
submit_btn = st.button(
    "💾 提交测评结果",
    use_container_width=True,
    type="primary",
    disabled=not is_ready
)

if submit_btn:
    # 构建提交记录
    moral_details = {dim: st.session_state[f"score_{dim}"] for dim in MORAL_DIMENSIONS}
    teaching_details = {dim: st.session_state[f"score_{dim}"] for dim in TEACHING_DIMENSIONS}
    
    submit_record = {
        "测评时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "被测评人": st.session_state["selected_person"],
        "测评人身份": st.session_state["evaluator_role"],
        "师德表现各维度得分": moral_details,
        "教学业绩各维度得分": teaching_details,
        "师德表现平均分": moral_avg,
        "教学业绩平均分": teaching_avg,
        "最终综合得分": final_score,
        "权重配置": f"师德{MEVAL_WEIGHT*100}%+教学{TEACHING_WEIGHT*100}%"
    }
    
    # 保存记录
    try:
        save_data(submit_record)
        st.session_state.submission_success = True
        st.session_state.submission_info = {
            "person": st.session_state["selected_person"],
            "score": final_score,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 提交成功后重置所有输入值（归零）
        for dim in MORAL_DIMENSIONS + TEACHING_DIMENSIONS:
            st.session_state[f"score_{dim}"] = 0.0
        st.session_state["selected_person"] = ""
        st.session_state["evaluator_role"] = ""
        
    except Exception as e:
        st.error(f"❌ 提交失败：{str(e)}")

# 7. 提交成功提示（显示在最下方）
st.markdown("---")
if st.session_state.submission_success:
    success_info = st.session_state.submission_info
    st.success(f"""🎉 测评结果提交成功！
    被测评人：{success_info['person']}
    最终综合得分：{success_info['score']} 分
    提交时间：{success_info['time']}
    所有分值已自动归零，可继续为下一位测评~
    """)
    # 重置提交状态
    st.session_state.submission_success = False
    st.session_state.submission_info = {}

# 手机端操作提示（最底部）
st.caption("💡 操作小贴士：输入分值后实时显示结果，所有维度填完后提交按钮自动启用，点击即提交并归零~")

# ===================== 管理员专属功能区 =====================
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
