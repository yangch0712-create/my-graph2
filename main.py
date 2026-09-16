import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling cards, insights, and headers
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 4px solid #ff4b4b;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .insight-box {
        background-color: #f0f7ff;
        border-left: 5px solid #1e88e5;
        padding: 16px;
        border-radius: 6px;
        margin-top: 12px;
        margin-bottom: 25px;
    }
    .insight-title {
        font-weight: bold;
        color: #1565c0;
        margin-bottom: 6px;
        font-size: 1.05rem;
    }
    .insight-content {
        color: #2c3e50;
        font-size: 0.98rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_movie_data():
    """Load data from remote CSV and process genres & dates."""
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # Process genre: Keep only the first genre if multiple are separated by '|'
    if 'genre' in df.columns:
        df['genre'] = df['genre'].apply(
            lambda x: str(x).split('|')[0].strip() if pd.notnull(x) and str(x).strip() != '' else '미상'
        )

    # Convert numeric columns safely
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Date handling
    if 'openDt' in df.columns:
        df['openDt_str'] = df['openDt'].astype(str)

    return df


# Load dataset
df_raw = load_movie_data()

# App Header
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 TOP 10에 오른 개봉 영화 216편의 데이터 시각화 분석")

# Sidebar Filtering Options
st.sidebar.header("🔍 데이터 필터링")

# Genre filter
all_genres = sorted(list(df_raw['genre'].unique()))
selected_genres = st.sidebar.multiselect(
    "장르 선택",
    options=all_genres,
    default=all_genres
)

# Top 10 days slider filter
min_days, max_days = int(df_raw['days_in_top10'].min()), int(df_raw['days_in_top10'].max())
days_range = st.sidebar.slider(
    "Top 10 유지 기간 (일)",
    min_value=min_days,
    max_value=max_days,
    value=(min_days, max_days)
)

# Apply filters
df_filtered = df_raw[
    (df_raw['genre'].isin(selected_genres)) &
    (df_raw['days_in_top10'] >= days_range[0]) &
    (df_raw['days_in_top10'] <= days_range[1])
]

# Metric Summary Cards
st.markdown("### 📊 주요 요약 지표")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(label="분석 대상 영화 수", value=f"{len(df_filtered):,} 편")
with m2:
    avg_audi = df_filtered['total_audi'].mean() if len(df_filtered) > 0 else 0
    st.metric(label="평균 누적 관객수", value=f"{int(avg_audi):,} 명")
with m3:
    max_scrn = df_filtered['first_scrn'].max() if len(df_filtered) > 0 else 0
    st.metric(label="최대 개봉 스크린수", value=f"{int(max_scrn):,} 개")
with m4:
    avg_top10 = df_filtered['days_in_top10'].mean() if len(df_filtered) > 0 else 0
    st.metric(label="평균 Top10 유지일", value=f"{avg_top10:.1f} 일")

st.divider()


# Graph 1: Donut Chart - Genre Distribution
st.subheader("1. 장르별 영화 편수 비율 (도넛 그래프)")

if not df_filtered.empty:
    genre_counts = df_filtered['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']

    fig1 = px.pie(
        genre_counts,
        names='장르',
        values='편수',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="장르별 개봉 영화 비중"
    )

    # Format hover text: count and percentage
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )

    fig1.update_layout(
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

# Insight Section for Graph 1
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    <div class="insight-content">
        박스오피스 상위권에 진입한 영화 중 특정 대표 장르(드라마, 액션, 애니메이션 등)의 편수 비중과 분포 상태를 한눈에 파악할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# Graph 2: Relationship between First Day Screens & Total Audiences
st.subheader("2. 개봉일 스크린수와 총 관객수의 관계 (산점도)")

if not df_filtered.empty:
    fig2 = px.scatter(
        df_filtered,
        x='first_scrn',
        y='total_audi',
        color='genre',
        size='first_week_audi',
        hover_name='movieNm',
        hover_data={
            'first_scrn': ':,',
            'total_audi': ':,',
            'days_in_top10': True,
            'genre': False
        },
        labels={
            'first_scrn': '개봉일 스크린수 (개)',
            'total_audi': '총 관객수 (명)',
            'genre': '장르',
            'first_week_audi': '개봉 첫 주 관객수'
        },
        title="스크린수 확보량과 흥행 성과간의 상관관계"
    )

    fig2.update_layout(
        height=500,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    st.plotly_chart(fig2, use_container_width=True)

# Insight Section for Graph 2
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    <div class="insight-content">
        개봉일 스크린수가 많을수록 최종 누적 관객수가 증가하는 경향을 보이지만, 초기 스크린수 대비 높은 상행 곡선을 그린 의외의 대흥행작도 함께 확인할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# Graph 3: Days in Top 10 Distribution across Genres (Box Plot)
st.subheader("3. 장르별 Top 10 생존 기간 분포 (박스 플롯)")

if not df_filtered.empty:
    fig3 = px.box(
        df_filtered,
        x='genre',
        y='days_in_top10',
        color='genre',
        points="all",
        hover_name='movieNm',
        labels={
            'genre': '장르',
            'days_in_top10': 'Top 10 머문 날수 (일)'
        },
        title="장르에 따른 10위권 유지 기간의 분포 및 이상치"
    )

    fig3.update_layout(
        showlegend=False,
        height=450,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    st.plotly_chart(fig3, use_container_width=True)

# Insight Section for Graph 3
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    <div class="insight-content">
        장르별로 박스오피스 Top 10 장기 흥행 지속력의 중앙값과 범위를 비교하여, 장기 흥행형 장르와 단기 집중형 장르의 차이를 파악할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# Graph 4: First Week Audiences vs Total Audiences Ratio Analysis
st.subheader("4. 개봉 첫 주 관객 대비 총 관객수 (입소문 흥행력)")

if not df_filtered.empty:
    df_filtered_calc = df_filtered.copy()
    df_filtered_calc['holdover_ratio'] = (
        df_filtered_calc['total_audi'] / df_filtered_calc['first_week_audi'].replace(0, 1)
    ).round(2)

    fig4 = px.bar(
        df_filtered_calc.sort_values(by='total_audi', ascending=False).head(15),
        x='movieNm',
        y='total_audi',
        color='holdover_ratio',
        color_continuous_scale='Reds',
        labels={
            'movieNm': '영화명',
            'total_audi': '총 관객수 (명)',
            'holdover_ratio': '첫주 대비 누적 배율'
        },
        title="상위 15개 흥행작의 개봉 첫 주 대비 지속 흥행 배율"
    )

    fig4.update_layout(
        xaxis_tickangle=-45,
        height=500,
        margin=dict(t=40, b=80, l=20, r=20)
    )

    st.plotly_chart(fig4, use_container_width=True)

# Insight Section for Graph 4
st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
    <div class="insight-content">
        개봉 첫 주 성적 대비 최종 총 관객수의 비율을 파악함으로써, 초반 마케팅 효과로 흥행한 영화와 지속적인 뒷심(입소문)으로 장기 흥행에 성공한 영화를 구분할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)


# Raw Data View Toggle
with st.expander("📄 원본 데이터 탐색하기"):
    st.dataframe(
        df_filtered[['movieCd', 'movieNm', 'openDt', 'genre', 'nation', 'first_scrn', 'total_audi', 'days_in_top10']],
        use_container_width=True
    )
