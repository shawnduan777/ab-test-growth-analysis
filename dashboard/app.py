
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# -------------------------
# 1. 页面设置
# -------------------------
st.set_page_config(
    page_title="A/B Test Growth Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("A/B Test Growth Dashboard")
st.caption(
    "电商 App 个性化商品推荐模块实验分析｜模拟数据，仅用于项目展示"
)

# -------------------------
# 2. 读取现有 SQL 结果
# -------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_DIR / "data"

@st.cache_data
def load_results():
    files = {
        "funnel": "funnel_results.csv",
        "retention": "retention_results.csv",
        "revenue": "revenue_results.csv",
        "profit": "profit_results.csv",
    }

    data = {}
    for name, filename in files.items():
        path = RESULTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"找不到结果文件：{path}")
        data[name] = pd.read_csv(path)

    return data

try:
    results = load_results()
except Exception as e:
    st.error(f"读取数据失败：{e}")
    st.info("请确认 data 文件夹中已放入四份 SQL 导出 CSV。")
    st.stop()

funnel = results["funnel"].copy()
retention = results["retention"].copy()
revenue = results["revenue"].copy()
profit = results["profit"].copy()

# 默认使用当前项目的两组实验结果
group_col = "experiment_group"
groups = funnel[group_col].astype(str).tolist()

if len(groups) < 2:
    st.error("漏斗结果中没有找到两组实验数据，请检查 CSV。")
    st.stop()

# 尽量识别 A/B 组；否则按 CSV 中的顺序展示
def find_group(keys):
    for group in groups:
        if any(key.lower() in group.lower() for key in keys):
            return group
    return None

control = find_group(["control", "group a", "a"])
treatment = find_group(["treatment", "group b", "b"])

if control is None or treatment is None or control == treatment:
    control, treatment = groups[0], groups[1]

def get_value(df, group, column):
    row = df[df[group_col].astype(str) == str(group)]
    if row.empty or column not in row.columns:
        return None
    return float(row.iloc[0][column])

# -------------------------
# 3. 实验概览
# -------------------------
st.header("一、实验概览")

a_rate = get_value(funnel, control, "overall_conversion_pct")
b_rate = get_value(funnel, treatment, "overall_conversion_pct")

if a_rate is None or b_rate is None:
    st.error("未能读取整体转化率，请检查 funnel_results.csv 字段。")
    st.stop()

difference = b_rate - a_rate
relative_lift = difference / a_rate * 100 if a_rate else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "对照组首单转化率",
    f"{a_rate:.2f}%",
)
c2.metric(
    "实验组首单转化率",
    f"{b_rate:.2f}%",
    delta=f"{difference:+.2f} 个百分点",
)
c3.metric(
    "相对提升",
    f"{relative_lift:+.2f}%",
)
c4.metric(
    "主指标 p 值",
    "0.1995",
    delta="未达到 5% 显著性水平",
    delta_color="off",
)

st.info(
    "实验结论：实验组的观测首单转化率更高，但差异未达到 "
    "5% 显著性水平。目前没有充分证据证明推荐模块提升了首单转化率。"
)

with st.expander("查看实验设计"):
    st.markdown("""
    - 实验对象：新注册用户
    - 对照组：现有首页
    - 实验组：首页增加个性化商品推荐模块
    - 分组比例：1:1
    - 计划样本量：约 26,000 人
    - 主指标：注册后 7 日内首单转化率
    - 显著性水平：5%，双侧检验
    - 以上为模拟实验，不代表真实业务效果
    """)

# -------------------------
# 4. 主指标可视化
# -------------------------
st.header("二、主指标对比")

primary = pd.DataFrame({
    "实验组": [control, treatment],
    "首单转化率（%）": [a_rate, b_rate],
}).set_index("实验组")

st.bar_chart(primary)

st.caption(
    "两组转化率差的 95% 置信区间约为 "
    "−0.24 至 +1.13 个百分点，包含 0，"
    "与当前不显著的统计检验结论一致。"
)

# -------------------------
# 5. 用户行为漏斗
# -------------------------
st.header("三、用户行为漏斗")

funnel_metrics = {
    "click_rate_pct": "点击率",
    "cart_conversion_pct": "点击后加购率",
    "payment_conversion_pct": "加购后支付率",
}

available_metrics = [
    (col, label)
    for col, label in funnel_metrics.items()
    if col in funnel.columns
]

if available_metrics:
    chart_data = funnel.set_index(group_col)[
        [col for col, _ in available_metrics]
    ].T
    chart_data.index = [
        funnel_metrics[col] for col, _ in available_metrics
    ]
    st.bar_chart(chart_data)
    st.dataframe(
        funnel[[group_col] + [col for col, _ in available_metrics]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("漏斗指标字段不匹配，请检查 funnel_results.csv。")

st.markdown("""
**业务解读：** 当前模拟结果中，实验组点击率更高，
但点击后的加购率和加购后的支付率没有明显改善。
后续可重点关注推荐点击之后的商品匹配度与购买转化。
""")

# -------------------------
# 6. 留存分析
# -------------------------
st.header("四、用户留存")

retention_metrics = {
    "d1_retention_pct": "D1 留存率",
    "d7_retention_pct": "D7 留存率",
}

available_retention = [
    col for col in retention_metrics if col in retention.columns
]

if available_retention:
    retention_chart = retention.set_index(group_col)[
        available_retention
    ].T
    retention_chart.index = [
        retention_metrics[col] for col in available_retention
    ]
    st.bar_chart(retention_chart)

    st.dataframe(
        retention,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("留存指标字段不匹配，请检查 retention_results.csv。")

# -------------------------
# 7. 收入与贡献利润
# -------------------------
st.header("五、业务价值")

business = revenue[
    [group_col, "arpu", "aov"]
].merge(
    profit[
        [group_col, "contribution_profit_per_user"]
    ],
    on=group_col,
    how="inner",
)

business_chart = business.set_index(group_col)[
    ["arpu", "aov", "contribution_profit_per_user"]
].T

business_chart.index = [
    "每用户平均收入 ARPU",
    "客单价 AOV",
    "每用户贡献利润",
]

st.bar_chart(business_chart)

st.dataframe(
    business,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "注意：收入与贡献利润目前仅作描述性比较，尚未进行统计检验；"
    "也未扣除推荐模块的实际开发和维护成本。"
)

# -------------------------
# 8. 退款率护栏指标
# -------------------------
st.header("六、业务护栏指标")

if "refund_order_rate_pct" in profit.columns:
    refund_chart = profit.set_index(group_col)[
        ["refund_order_rate_pct"]
    ].rename(columns={
        "refund_order_rate_pct": "退款订单率（%）"
    })

    st.bar_chart(refund_chart)

    st.dataframe(
        profit[
            [
                group_col,
                "refunded_orders",
                "refund_order_rate_pct",
                "refund_amount_rate_pct",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.warning(
    "实验组退款订单率的观测值较高，但当前尚未检验两组差异的统计显著性，"
    "不能直接认定推荐模块导致退款率上升。"
)

# -------------------------
# 9. 总结
# -------------------------
st.header("七、分析结论与建议")

st.markdown("""
1. 实验组的点击率和首单转化率观测值更高，但主指标差异未达到统计显著。
2. 点击率的提升尚未转化为明确的整体购买转化改善。
3. 实验组的收入与贡献利润观测值更高，但还需要统计检验和成本核算。
4. 应持续关注退款率等护栏指标，并进一步验证推荐模块的实际业务价值。
5. 当前结果不足以支持直接全面推广，建议继续实验或优化下游转化环节。
""")

st.caption(
    "数据来源：本项目模拟数据及 MySQL 导出的分析结果。"
)
