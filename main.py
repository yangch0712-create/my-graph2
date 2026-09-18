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

    # 제작 국가 결측치 처리
    df["nation"] = df["nation"].fillna("기타").astype(str)

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

st.divider()

# ----------------------------------------------------
# 네 번째 그래프: 개봉일 스크린수 vs 총 관객수 (산점도)
# ----------------------------------------------------
st.subheader("4. 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객수 산점도",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객수(명)",
        "genre": "장르",
    },
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명"
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린수가 많을수록 총 관객수도 대체로 증가하는 양(+)의 상관관계를 보이며, 초기 스크린 확보가 흥행의 주요 요소임을 알 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 다섯 번째 그래프: 장르별 총 관객수 분포 (박스플롯)
# ----------------------------------------------------
st.subheader("5. 주요 장르별 총 관객수 분포 (영화 10편 이상)")

# 영화 수가 10편 이상인 장르만 필터링
genre_counts_series = df["genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df["genre"].isin(top_genres)]

fig5 = px.box(
    df_filtered,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    points="outliers",
    title="주요 장르별 총 관객수 상자 그림 (Outliers 표출)",
    labels={"genre": "장르", "total_audi": "총 관객수(명)"},
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{x}<br>관객수: %{y:,}명"
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "장르별 중앙값 차이 외에도 상자 밖으로 크게 튀어나온 이상치(Outlier) 점들을 통해 특정 장르 내 대형 흥행 성공작의 존재 여부와 흥행 편차를 한눈에 확인할 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 여섯 번째 그래프: 개봉일 스크린수 vs 총 관객수 (버블 차트 - 크기: 첫 주 관객수)
# ----------------------------------------------------
st.subheader("6. 개봉일 스크린수, 총 관객수, 첫 주 관객수의 관계 (버블 차트)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={"first_week_audi": ":,"},
    size_max=50,
    title="개봉일 스크린수 vs 총 관객수 (버블 크기: 첫 주 관객수)",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객수(명)",
        "first_week_audi": "첫 주 관객수(명)",
        "genre": "장르",
    },
)

fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{customdata[0]:,}명"
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린수와 총 관객수가 높은 우상향 영역일수록 버블 크기(첫 주 관객수)도 함께 커지며, 초반 흥행 성공(첫 주 관객)이 최종 총 관객수 형성의 핵심 동인임을 확인할 수 있습니다."
)

st.divider()

# ----------------------------------------------------
# 일곱 번째 그래프: 국가 -> 장르 선버스트 (크기: 영화 편수)
# ----------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트)")

# 선버스트 차트 계층: 제작 국가(nation) -> 장르(genre)
fig7 = px.sunburst(
    df,
    path=["nation", "genre"],
    title="제작 국가 및 장르별 영화 편수 선버스트 차트",
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentParent:.1%}"
)

st.plotly_chart(fig7, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "주요 제작 국가별 영화 점유율과 함께, 각 국가에서 주력으로 제작/수입하는 주요 장르 구성을 다층 계층 구조로 명확하게 비교해 볼 수 있습니다."
)
