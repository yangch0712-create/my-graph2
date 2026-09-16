import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("KOBIS 박스오피스 데이터를 바탕으로 영화 수, 분포, 변수 간의 관계를 시각화합니다.")
st.divider()

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 열에서 세로막대(|) 기호로 나누어진 여러 장르 중 첫 번째 장르만 추출
    df['genre_first'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0] if x != 'nan' else '기타')
    
    return df

df = load_data()

# ---------------------------------------------------------
# 그래프 1: 장르별 영화 편수 (도넛 차트)
# ---------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

# 장르별 빈도 계산
genre_counts = df['genre_first'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.4,
    title="장르별 영화 비율",
    labels={'장르': '장르', '편수': '영화 편수'}
)

# 마우스오버 시 편수와 비율이 보이도록 설정
fig1.update_traces(
    textinfo='percent+label',
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 구역
with st.container():
    st.markdown("#### 💡 이 그래프로 알 수 있는 것")
    st.info("박스오피스 상위권 영화 중 특정 장르(예: 드라마다 액션 등)가 차지하는 비중과 편수 분포를 한눈에 비교할 수 있습니다.")

st.divider()
