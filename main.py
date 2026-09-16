import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 열 전처리: 세로막대 기호(|)로 여러 개 구분된 경우 첫 번째 장르만 추출
    df["genre"] = df["genre"].fillna("미상").astype(str)
    df["genre"] = df["genre"].apply(lambda x: x.split("|")[0].strip())

    return df


df = load_data()

# ----------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 (도넛 그래프)
# ----------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_counts,
    values="영화 편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 비율",
)
fig1.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "특정 주요 장르가 전체 개봉 영화의 과반수 이상을 차지하는 비대칭적 분포 형태를 보입니다."
)

st.divider()

# ----------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객수 (트리맵)
# ----------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객수 분포")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 영화"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객수 트리맵",
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명",
    texttemplate="%{label}",
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "같은 장르 내에서도 특정 블록버스터 영화가 총 관객수의 대부분을 차지하는 흥행 편중 현상을 확인할 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 세 번째 그래프: 총 관객수 분포 (히스토그램)
# ----------------------------------------------------
st.subheader("3. 총 관객수 분포")

# 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객수 히스토그램",
    labels={"total_audi": "총 관객수(명)", "count": "영화 수"},
)
fig3.update_traces(hovertemplate="관객수 구간: %{x}<br>영화 수: %{y}편")
fig3.update_layout(yaxis_title="영화 수")

st.plotly_chart(fig3, use_container_width=True)

# 데이터 기반 수치 계산 (가장 관객이 많은 영화)
max_movie = df.loc[df["total_audi"].idxmax()]
max_movie_name = max_movie["movieNm"]
max_movie_audi = max_movie["total_audi"]

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 **100만 명 미만(하위 구간)**에 밀집되어 있는 전형적인 오른쪽 꼬리가 긴(Right-Skewed) 분포를 보이며, "
    f"가장 관객이 많은 영화는 **'{max_movie_name}'**(약 {max_movie_audi:,.0f}명)입니다."
)
