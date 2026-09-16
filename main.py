import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 타이틀 및 설명
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("1년간 박스오피스 10위권에 든 한국/외국 영화 216편의 개봉 및 관객 데이터 분석")
st.divider()

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 전처리: 세로막대 기호(|)로 분리된 장르 중 첫 번째 장르만 사용
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    
    return df

df = load_data()

# ---------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 (도넛 차트)
# ---------------------------------------------------------
st.header("1. 장르별 영화 편수 비율")

# 장르별 편수 계산
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

# Plotly 도넛 차트 생성
fig_donut = px.pie(
    genre_counts, 
    values='count', 
    names='genre', 
    hole=0.4,
    title="장르별 영화 편수 분포",
    labels={'genre': '장르', 'count': '영화 편수'}
)

# 호버 툴팁 및 그래프 레이아웃 설정
fig_donut.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}"
)
fig_donut.update_layout(
    margin=dict(t=50, b=20, l=20, r=20),
    height=500
)

st.plotly_chart(fig_donut, use_container_width=True)

# 인사이트 구역
with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 영화 중 특정 인기 장르(예: 애니메이션, 액션, 드라마다 등)가 전체 편수의 대부분을 차지하는 편중 현상을 한눈에 파악할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객 수")

# Plotly 트리맵 생성
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), 'genre', 'movieNm'],
    values='total_audi',
    color='total_audi',
    color_continuous_scale='Blues',
    title="장르 및 영화별 총 관객 수 분포 (타일 크기 = 총 관객 수)"
)

# 호버 툴팁 설정
fig_treemap.update_traces(
    hovertemplate="<b>영화명:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명<extra></extra>"
)

fig_treemap.update_layout(
    margin=dict(t=50, b=20, l=20, r=20),
    height=600
)

st.plotly_chart(fig_treemap, use_container_width=True)

# 인사이트 구역
with st.container():
    st.info("💡 **이 그래프로 알 수 있는 것:** 전체 관객 수에서 각 장르 및 개별 영화가 차지하는 비중을 직관적으로 비교할 수 있으며, 박스오피스 상위 영화들이 시장 전체 흥행을 얼마나 견인했는지 파악할 수 있습니다.")
