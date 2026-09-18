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

    # openDt(개봉일) 파싱 및 계절 컬럼 생성
    df["openDt_str"] = df["openDt"].astype(str)
    df["open_date"] = pd.to_datetime(df["openDt_str"], format="%Y%m%d", errors="coerce")

    # 만약 포맷이 안 맞는 경우 자동 처리
    if df["open_date"].isna().all():
        df["open_date"] = pd.to_datetime(df["openDt_str"], errors="coerce")

    df["month"] = df["open_date"].dt.month

    # 계절 매핑 함수
    def get_season(month):
        if month in [3, 4, 5]:
            return "봄 (3~5월)"
        elif month in [6, 7, 8]:
            return "여름 (6~8월)"
        elif month in [9, 10, 11]:
            return "가을 (9~11월)"
        elif month in [12, 1, 2]:
            return "겨울 (12~2월)"
        else:
            return "기타"

    df["season"] = df["month"].apply(get_season)

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
    "같은 장르 내에서도 특정 영화가 관객수를 다수 차지하고 있다는 것을 볼 수 있고, 한 장르에 속한 영화가 다른 장르에 비해 공급된 영화 수가 부족하더라도 스타성이 있고 사람들이 많이 찾는다면 그만큼 공간을 많이 차지한다는 것을 확인할 수 있다.."
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
    "총 관객 수가 많은 탑 영화가 적은 만큼 총 관객수가 높게 측정되면 그에 따른 영화 편수도 작다는 것을 볼 수 있다. 그래서 그만큼히스토그램 넓이는 총 관객수가 적다는 척도를 나타내는 맨 왼쪽이 가장 넓은 것을 알 수 있다. (영화도 약육강식의 세계)"
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
    "개봉일 스크린수가 많을수록 총 관객수도 대체로 증가하는 양(+)의 상관관계를 보이지만, 아바타:불과 재와 왕과 사는 남자를 비교했을 때 상대적으로 스크린수가 많지만 관객 수가 적어 보일 수도 있고, 상대적으로 스크린수가 적지만 관객 수가 많아 보일 수도 있다."
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
    "평균, 중앙값을 나타내는 박스 외의 이상치(값 중에서도 평균에 비해 크게 동 떨어져 있는 값)를 통해 3번에서 보았던 히스토그램의 확장판을 보는 느낌이다. 장르별로 세분화를 함으로써 해당 장르에서 가장 많이 사랑받은 영화를 보고, 영화 시장에서는 그런 작품을 확인함으로써 대중의 반응을 볼 수 있다."
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
    "보통 개봉일 스크린수가 많을 수록 총 관객수가 많은 양의 상관관계를 보인다. 그 중에서도 애니메이션/액션/어드벤처/판타지가 총 관객수가 다른 장르에 비해 혼자 많은 것을 볼 수 있는데 이는 장르의 특성 상 아이 혼자 뿐만이 아니라 아이를 보기 위해 같이 오는 가족 때문에 총 관객수가 높게 집계된 것으로 보인다."
)

st.divider()

# ----------------------------------------------------
# 일곱 번째 그래프: 국가 -> 장르 선버스트 (크기: 영화 편수)
# ----------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트)")

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
    "국가별 나온 것들 중 가장 잘 보이는 영화의 장르를 통해 어떤 나라가 어떤 장르에 특화되어 있는지, 자신이 있는지 등을 알 수 있다. 일본의 경우 애니메이션으로 유명한 지브리 스튜디오, 한국 같은 경우에는 사랑의 하츄핑같은 애니메이션이나 서정적인 로맨스 혹은 가족애를 중점으로 하는 드라마에 강점이 있는 것을 확인할 수 있다. "
)

st.divider()

# ----------------------------------------------------
# 여덟 번째 그래프: 계절별 영화 트리맵
# ----------------------------------------------------
st.subheader("8. 계절별 사람들이 많이 찾는 영화는 무엇인가")

# 트리맵 생성 (계층 구조: 계절 -> 영화명, 크기: 총 관객수)
fig8 = px.treemap(
    df,
    path=[px.Constant("전체 계절"), "season", "movieNm"],
    values="total_audi",
    title="계절별 사람들이 많이 찾는 영화는 무엇인가",
)

# 마우스오버 시 계절/영화명과 총 관객수가 표시되도록 설정
fig8.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명",
    texttemplate="%{label}",
)

st.plotly_chart(fig8, use_container_width=True)

st.markdown("##### 📌 이 그래프로 알 수 있는 것")
st.write(
    "여름과 겨울 등 극장을 많이 찾는 성수기에 개봉한 특정 초대형 흥행작(홍보를 많이 한 것 등)이 전체 관객수의 상당 비중을 차지하며, 계절별 흥행한 자굼의 규모를 한 눈에 파악할 수 있다. 또한, 이것으로 유사한 영화 연말정산을 해볼 수 있다."
)
