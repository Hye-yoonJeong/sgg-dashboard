"""
전국 시군구 생활SOC 현황 대시보드
Korean SGG Living Infrastructure Dashboard
With Interactive Map - Native Streamlit Components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ========== Page Config ==========
st.set_page_config(
    page_title="생활SOC 현황 대시보드",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ========== Custom CSS ==========
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    .stApp {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    p, span, label {
        color: #e0e0e0 !important;
    }
    
    .section-title {
        color: #667eea !important;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #667eea;
    }
    
    .region-name {
        font-size: 1.5rem;
        font-weight: 900;
        color: #fff !important;
        margin-bottom: 4px;
    }
    
    .region-sub {
        font-size: 0.9rem;
        color: #888 !important;
    }
    
    .pop-decrease {
        background: rgba(224, 122, 95, 0.2);
        color: #E07A5F !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .pop-stable {
        background: rgba(90, 125, 154, 0.2);
        color: #5A7D9A !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.02);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #888;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 126, 234, 0.2) !important;
        color: #667eea !important;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #fff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #fff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #888;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ========== Data Loading ==========
@st.cache_data
def load_geojson():
    with open("data/SGG_Full_Data_4326_tol100.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    return geojson_data


@st.cache_data
def load_data():
    geojson_data = load_geojson()

    # GeoJSON features를 DataFrame으로 변환
    records = []
    for feature in geojson_data["features"]:
        records.append(feature["properties"])

    df = pd.DataFrame(records)

    # 계산 필드 추가
    df["FACILITY_TOTAL_24"] = (
        df["LIV_24"]
        + df["MED_24"]
        + df["CARE_24"]
        + df["EDU_24"]
        + df["CUL_24"]
        + df["SPT_24"]
    )
    df["FACILITY_TOTAL_15"] = (
        df["LIV_15"]
        + df["MED_15"]
        + df["CARE_15"]
        + df["EDU_15"]
        + df["CUL_15"]
        + df["SPT_15"]
    )

    return df


@st.cache_data
def get_geojson_dict():
    return load_geojson()


# ========== Load Data ==========
try:
    df = load_data()
    geojson_data = get_geojson_dict()
except Exception as e:
    st.error(f"데이터 파일을 찾을 수 없습니다: {e}")
    st.stop()


# ========== Helper Functions ==========
def format_number(n, decimal=0):
    if pd.isna(n):
        return "-"
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    elif n >= 1000:
        return f"{n/1000:.1f}K"
    else:
        if decimal > 0:
            return f"{n:.{decimal}f}"
        return f"{int(n):,}"


def display_info_table(data_dict):
    """Display info table using native Streamlit components"""
    for label, value in data_dict.items():
        cols = st.columns([1.2, 0.8])
        with cols[0]:
            st.caption(label)
        with cols[1]:
            st.write(f"**{value}**")


def get_summary_stats(data, use_average=False):
    """Calculate summary statistics for a group"""
    if use_average:
        stats = {
            "시군구 수": len(data),
            "평균 인구": format_number(data["POP_23"].mean()),
            "평균 인구밀도": f"{data['PDEN_23'].mean():.1f}",
            "평균 가구수": format_number(data["HHLD_23"].mean()),
            "평균 통근시간": f"{data['COM_T_20'].mean():.1f}분",
        }
    else:
        stats = {
            "시군구 수": len(data),
            "총 인구": format_number(data["POP_23"].sum()),
            "평균 인구밀도": f"{data['PDEN_23'].mean():.1f}",
            "총 가구수": format_number(data["HHLD_23"].sum()),
            "평균 통근시간": f"{data['COM_T_20'].mean():.1f}분",
        }
    return stats


def get_facility_stats(data, use_average=False):
    """Calculate facility statistics"""
    if use_average:
        stats = {
            "생활시설 (LIV)": format_number(data["LIV_23"].mean()),
            "의료시설 (MED)": format_number(data["MED_23"].mean()),
            "돌봄시설 (CARE)": format_number(data["CARE_23"].mean()),
            "교육시설 (EDU)": format_number(data["EDU_23"].mean()),
            "문화시설 (CUL)": format_number(data["CUL_23"].mean()),
            "체육시설 (SPT)": format_number(data["SPT_23"].mean()),
        }
    else:
        stats = {
            "생활시설 (LIV)": format_number(data["LIV_23"].sum()),
            "의료시설 (MED)": format_number(data["MED_23"].sum()),
            "돌봄시설 (CARE)": format_number(data["CARE_23"].sum()),
            "교육시설 (EDU)": format_number(data["EDU_23"].sum()),
            "문화시설 (CUL)": format_number(data["CUL_23"].sum()),
            "체육시설 (SPT)": format_number(data["SPT_23"].sum()),
        }
    return stats


# ========== Session State ==========
if "selected_sigungu" not in st.session_state:
    st.session_state.selected_sigungu = None


# ========== Header ==========
st.markdown(
    """
<div style="padding: 10px 0 20px 0;">
    <h1 style="font-size: 1.8rem; margin-bottom: 4px;">
        🏘️ 전국 시군구 생활SOC 현황 대시보드
    </h1>
    <p style="color: #666; font-size: 0.9rem; margin: 0;">
        2015-2024 생활인프라 시설 및 인구 변화 분석 · 시군구를 클릭하여 상세정보 확인
    </p>
</div>
""",
    unsafe_allow_html=True,
)


# ========== Layout ==========
col_map, col_info = st.columns([1.4, 0.6])

with col_map:
    # Map visualization
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations="SIGUNGU_CD",
        featureidkey="properties.SIGUNGU_CD",
        color="POP_DEC_LB",
        color_discrete_map={"인구감소지역": "#E07A5F", "비인구감소지역": "#5A7D9A"},
        mapbox_style="carto-darkmatter",
        center={"lat": 36.5, "lon": 127.8},
        zoom=5.8,
        opacity=0.7,
        hover_name="SIGUNGU_NM",
        hover_data={
            "SIDO_NM": True,
            "POP_DEC_LB": True,
            "POP_23": ":,.0f",
            "PDEN_23": ":.1f",
            "COM_T_20": ":.1f",
        },
        labels={
            "SIDO_NM": "시도",
            "POP_DEC_LB": "지역유형",
            "POP_23": "인구(2023)",
            "PDEN_23": "인구밀도",
            "COM_T_20": "평균통근시간",
        },
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR"),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(color="white", size=11),
            title="",
        ),
        height=500,
    )

    # Capture click events
    selected = st.plotly_chart(
        fig, use_container_width=True, on_select="rerun", key="map"
    )

    # Process selection
    if selected and selected.selection and selected.selection.points:
        point = selected.selection.points[0]
        if "location" in point:
            st.session_state.selected_sigungu = point["location"]
        elif "pointIndex" in point:
            idx = point["pointIndex"]
            st.session_state.selected_sigungu = df.iloc[idx]["SIGUNGU_CD"]


with col_info:
    # View mode tabs
    tab1, tab2, tab3 = st.tabs(["📊 전국", "🔴 인구감소", "🔵 비인구감소"])

    with tab1:
        st.markdown('<p class="section-title">전국 현황</p>', unsafe_allow_html=True)
        total_stats = get_summary_stats(df)
        display_info_table(total_stats)

        st.markdown("---")
        st.markdown(
            '<p class="section-title">시설 현황 (2023)</p>', unsafe_allow_html=True
        )
        facility_stats = get_facility_stats(df)
        display_info_table(facility_stats)

    with tab2:
        st.markdown('<p class="section-title">인구감소지역</p>', unsafe_allow_html=True)
        pop_dec_df = df[df["POP_DEC_LB"] == "인구감소지역"]
        dec_stats = get_summary_stats(pop_dec_df, use_average=True)
        display_info_table(dec_stats)

        st.markdown("---")
        st.markdown(
            '<p class="section-title">시설 현황 (2023)</p>', unsafe_allow_html=True
        )
        dec_facility = get_facility_stats(pop_dec_df, use_average=True)
        display_info_table(dec_facility)

    with tab3:
        st.markdown(
            '<p class="section-title">비인구감소지역</p>', unsafe_allow_html=True
        )
        non_dec_df = df[df["POP_DEC_LB"] == "비인구감소지역"]
        non_stats = get_summary_stats(non_dec_df, use_average=True)
        display_info_table(non_stats)

        st.markdown("---")
        st.markdown(
            '<p class="section-title">시설 현황 (2023)</p>', unsafe_allow_html=True
        )
        non_facility = get_facility_stats(non_dec_df, use_average=True)
        display_info_table(non_facility)


# ========== Selected Region Detail ==========
st.markdown("---")

# Region selector
col_select, col_empty = st.columns([0.3, 0.7])
with col_select:
    sigungu_list = (df["SIDO_NM"] + " " + df["SIGUNGU_NM"]).tolist()
    selected_name = st.selectbox(
        "시군구 선택",
        options=["선택하세요"] + sigungu_list,
        index=0,
        label_visibility="collapsed",
    )

    if selected_name != "선택하세요":
        # "서울특별시 종로구" -> "종로구" 추출
        sigungu_nm = selected_name.split(" ")[-1]
        sido_nm = " ".join(selected_name.split(" ")[:-1])
        st.session_state.selected_sigungu = df[
            (df["SIDO_NM"] == sido_nm) & (df["SIGUNGU_NM"] == sigungu_nm)
        ]["SIGUNGU_CD"].values[0]

# Display selected region info
if st.session_state.selected_sigungu:
    region = df[df["SIGUNGU_CD"] == st.session_state.selected_sigungu].iloc[0]

    # Header
    pop_class = (
        "pop-decrease" if region["POP_DEC_LB"] == "인구감소지역" else "pop-stable"
    )

    st.markdown(
        f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <div>
            <div class="region-name">{region['SIGUNGU_NM']}</div>
            <div class="region-sub">{region['SIDO_NM']}</div>
        </div>
        <span class="{pop_class}">{region['POP_DEC_LB']}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Info columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<p class="section-title">기본 정보</p>', unsafe_allow_html=True)
        basic_info = {
            "면적": f"{region['AREA_KM2']:.1f} km²",
            "인구 (2023)": format_number(region["POP_23"]),
            "인구밀도": f"{region['PDEN_23']:.1f} 명/km²",
            "가구수 (2023)": format_number(region["HHLD_23"]),
            "평균 통근시간": f"{region['COM_T_20']:.1f}분",
            "통근 인구": format_number(region["COM_POP_20"]),
        }
        display_info_table(basic_info)

    with col2:
        st.markdown(
            '<p class="section-title">시설 현황 (2023)</p>', unsafe_allow_html=True
        )
        facility_info = {
            "생활시설": format_number(region["LIV_23"]),
            "의료시설": format_number(region["MED_23"]),
            "돌봄시설": format_number(region["CARE_23"]),
            "교육시설": format_number(region["EDU_23"]),
            "문화시설": format_number(region["CUL_23"]),
            "체육시설": format_number(region["SPT_23"]),
        }
        display_info_table(facility_info)

    with col3:
        st.markdown(
            '<p class="section-title">주거 현황 (2023)</p>', unsafe_allow_html=True
        )
        housing_info = {
            "아파트": format_number(region["HAPT_23"]),
            "단독주택": format_number(region["HDET_23"]),
            "다세대": format_number(region["HMULTI_23"]),
            "연립주택": format_number(region["HROW_23"]),
            "영업용건물내": format_number(region["HCOMM_23"]),
            "기타": format_number(region["HOTH_23"]),
        }
        display_info_table(housing_info)

    with col4:
        st.markdown(
            '<p class="section-title">통근 현황 (2020)</p>', unsafe_allow_html=True
        )
        commute_info = {
            "승용차 이용": format_number(region["COM_A_P_20"]),
            "승용차 시간": f"{region['COM_A_T_20']:.1f}분",
            "대중교통 이용": format_number(region["COM_T_P_20"]),
            "대중교통 시간": f"{region['COM_T_T_20']:.1f}분",
            "기타 이용": format_number(region["COM_O_P_20"]),
            "기타 시간": f"{region['COM_O_T_20']:.1f}분",
        }
        display_info_table(commute_info)

    # Time series charts
    st.markdown("<br>", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Population density trend
        years = list(range(2015, 2025))
        pden_values = [region[f"PDEN_{str(y)[2:]}"] for y in years]

        fig_pden = go.Figure()
        fig_pden.add_trace(
            go.Scatter(
                x=years,
                y=pden_values,
                mode="lines+markers",
                line=dict(color="#667eea", width=3),
                marker=dict(size=8, color="#667eea"),
                name="인구밀도",
            )
        )

        fig_pden.update_layout(
            title=dict(
                text="인구밀도 변화 (2015-2024)", font=dict(size=14, color="#fff")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            margin=dict(l=20, r=20, t=40, b=20),
            height=250,
            showlegend=False,
        )

        st.plotly_chart(fig_pden, use_container_width=True)

    with chart_col2:
        # Facility trend
        years = list(range(2015, 2025))
        liv_values = [region[f"LIV_{str(y)[2:]}"] for y in years]

        fig_liv = go.Figure()
        fig_liv.add_trace(
            go.Scatter(
                x=years,
                y=liv_values,
                mode="lines+markers",
                line=dict(color="#81c784", width=3),
                marker=dict(size=8, color="#81c784"),
                name="생활시설",
            )
        )

        fig_liv.update_layout(
            title=dict(
                text="생활시설 변화 (2015-2024)", font=dict(size=14, color="#fff")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            margin=dict(l=20, r=20, t=40, b=20),
            height=250,
            showlegend=False,
        )

        st.plotly_chart(fig_liv, use_container_width=True)

else:
    st.markdown(
        """
    <div style="text-align: center; padding: 40px; color: #666;">
        <p style="font-size: 1.2rem;">👆 지도에서 시군구를 클릭하거나 위 드롭다운에서 선택하세요</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ========== Footer ==========
st.markdown(
    """
<div style="text-align: center; padding: 30px 0 10px 0; color: #444; font-size: 0.75rem;">
    <p>Data: SGIS/KOSIS | Built with Streamlit & Plotly</p>
    <p>© 2026 서울대학교 USDL</p>
</div>
""",
    unsafe_allow_html=True,
)
