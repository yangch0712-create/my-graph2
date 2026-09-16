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
    "장르 별로 영화의 편수가 얼마나 많이 몰려있는지를 볼 수 있다. 영화 시장에서 어떤 장르가 선호되는지, 어떤 장르가 비선호되고 그만큼 공급이 적은지를 알 수 있다."
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
    "같은 장르 내에서도 특정 영화가 관객수를 다수 차지하고 있다는 것을 볼 수 있고, 한 장르에 속한 영화가 다른 장르에 비해 공급된 영화 수가 부족하더라도 스타성이 있고 사람들이 많이 찾는다면 그만큼 공간을 많이 차지한다는 것을 확인할 수 있다."
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
    " 이 공간은 깊은 생각을 해보고 다시 적어야 한당 "
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

# 마우스오버 스타일 지정
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명"
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린수가 많을수록 총 관객수도 대체로 증가하는 양(+)의 상관관계를 보이지만, 아바타:불과 재와 왕과 사는 남자를 비교했을 때 상대적으로 스크린수가 많지만 관객 수가 적어 보일 수도 있고, 상대적으로 스크린수가 적지만 관객 수가 많아 보일 수도 있다."
)
