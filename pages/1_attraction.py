# 터미널에서 실행: streamlit run app.py
import streamlit as st
from openai import OpenAI
import json

# OpenAI API 클라이언트 초기화
api_key = "sk-"
client = OpenAI(api_key=api_key)

# Attraction 클래스 정의
class Attraction:
    def __init__(self, name, category, address, phone, hours, description):
        self.name = name
        self.category = category
        self.address = address
        self.phone = phone
        self.hours = hours
        self.description = description

    def __repr__(self):
        return (f"Attraction(name='{self.name}', "
                f"category='{self.category}', address='{self.address}', "
                f"phone='{self.phone}', hours='{self.hours}', "
                f"description='{self.description}')")

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "description": self.description,
        }

# 명소 추천 함수
def get_related_Attractions(query, Attractions, client, model="gpt-4o-mini"):
    Attraction_data = [a.to_dict() for a in Attractions]

    messages = [
        {"role": "system", "content": "You are a helpful assistant for recommending attractions."},
        {"role": "user", "content": f"""
        아래는 명소 데이터입니다. 사용자가 '{query}'에 관련된 명소를 3개 추천해주세요.
        추천 결과는 JSON 형식으로 반환하며, 각 명소에는 다음 필드가 있어야 합니다:
        - name (명소 이름)
        - category (명소 종류)
        - address (주소)
        - phone (전화번호)
        - hours (운영 시간)
        - description (설명)

        JSON 형식으로만 답변해주세요. 예:
        [
            {{
                "name": "명1",
                "category": "역사",
                "address": "주소1",
                "phone": "전화번호1",
                "hours": "운영 시간1",
                "description": "설명1"
            }},
            ...
        ]

        명소 데이터:
        {Attraction_data}
        """}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    # 응답 내용 가져오기
    answer = response.choices[0].message.content

    # 불필요한 코드 블록 제거
    cleaned_answer = answer.strip("```").strip("json").strip()

    try:
        recommendations = json.loads(cleaned_answer)
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류: {e}")
        st.write(f"원본 응답: {answer}")  # 디버깅용 출력
        st.write(f"클린된 응답: {cleaned_answer}")  # 클린한 응답 확인
        return []

    return [
        Attraction(
            name=item["name"],
            category=item["category"],
            address=item["address"],
            phone=item["phone"],
            hours=item["hours"],
            description=item["description"]
        )
        for item in recommendations
    ]

if 'selected_Attractions' not in st.session_state:
    st.session_state['selected_Attractions'] = []

# Streamlit UI 구성
st.title("부산 명소 추천 시스템")

# 테스트용 명소 데이터
Attractions = [
    Attraction("명지철새탐조대", "자연", "부산 강서구 명지오션시티1로 284", "051-970-4000", "없음", "명지철새탐조대는 매년 150여 종의 겨울 철새가 찾는 도래지로, 갯벌에서 철새들의 생동감 넘치는 모습을 관찰할 수 있는 생태학습 명소입니다. 망원경과 안내 표지판이 마련되어 있어 탐조의 즐거움을 더하며, 일몰과 함께 황금빛 자연 풍경을 감상할 수 있는 힐링 장소로도 유명합니다."),
    Attraction("오시리아 해안 산책로", "자연", "부산광역시 기장군 기장읍 시랑리 62-22", "051-709-4000", "없음", "오시리아 해안 산책로는 2.1km의 코스에서 탁 트인 바다와 자연을 만끽할 수 있는 힐링 명소입니다. 해동용궁사와 용왕단 등 전설이 담긴 장소를 지나며 아름다운 경치와 함께 여유로운 산책을 즐길 수 있습니다."),
    Attraction("반여 초록공원 장산 계곡", "자연", "부산광역시 해운대구 반여동 산111-2", "051-749-4000(해운대구청)", "초록공원 롤러슬라이드: 매일 09:00~17:00", "반여 초록공원은 아이들과 자연을 만끽할 수 있는 숲속 놀이터로, 피크닉 존과 네트 놀이대, 롤러 슬라이드 등 다양한 시설이 마련되어 있습니다. 또한, 근처의 얕은 계곡에서 물놀이와 물고기 채집을 즐기며 여름을 시원하게 보낼 수 있는 장소입니다."),
    Attraction("친환경스카이웨이전망대", "자연", "부산광역시 동구 망양로 533-33", "051-441-3121", "없음", "부산의 산복도로와 망양로는 부산 바다와 구도심의 멋진 전망을 제공하며, 이곳의 집들은 옥상이 전망대로 사용되어 관광객의 눈길을 끕니다. 친환경스카이웨이전망대는 벚나무가 우거진 산비탈에서 부산항대교와 북항 등을 파노라마로 감상할 수 있는 최고의 전망 명소로, 밤에는 화려한 야경을 즐길 수 있습니다."),
    Attraction("흰여울문화마을", "자연", "부산광역시 영도구 흰여울길", "051-419-4067", "없음", "절영해안산책로와 흰여울문화마을은 가파른 절벽 끝에 위치한 독특한 마을로, 피난민들의 애환이 깃든 곳이자 현재는 문화예술마을로 변모한 장소입니다. 흰여울길은 아기자기한 카페와 공방들이 이어지며, 바다 풍경과 함께 여유로운 시간을 즐길 수 있는 명소입니다."),
    Attraction("해운대해수욕장", "자연", "부산광역시 해운대구 해운대해변로 264", "051-749-5700", "09:00~18:00", "해운대해수욕장은 부산을 대표하는 해수욕장으로, 여름에는 수많은 피서객이 몰리고, 다양한 오락시설과 부대시설이 잘 갖춰져 있어 방문객들에게 다이내믹한 분위기를 선사합니다. 또한, 동백섬과 동백해안산책로, 밤의 마린시티 풍경 등 해운대의 매력은 사계절 내내 변하지 않으며, 해운대 모래축제와 부산바다축제 등 다양한 행사도 인기입니다."),
    Attraction("송도구름다리", "자연", "부산광역시 서구 암남동 620-53", "051-240-4087", "09:00~17:00", "송도용궁구름다리는 18년 만에 복원되어 송도 바다의 멋진 풍경을 더욱 가까이에서 즐길 수 있는 명소입니다. 이 다리는 '행운의 열쇠' 모양으로 설계되어 사랑과 행운을 부른다고 전해지며, 밤에는 황금빛 조명이 켜져 더욱 매력적인 분위기를 자아냅니다. 다리 위에서 바라보는 송도의 바다와 기암, 초록의 자연은 특별한 경험을 선사하며, 암남공원의 숲길을 따라 산책도 즐길 수 있어 일상에서 벗어나 힐링을 할 수 있는 장소입니다."),
    Attraction("아미동 비석문화마을", "역사", "부산광역시 서구 아미로49", "없음", "없음", "아미동 비석문화마을은 6.25 전쟁 후 피난민들이 일본인 묘지 위에 집을 지으며 형성된 마을이다. 마을 곳곳에는 비석과 상석이 건축 자재로 사용된 흔적이 남아 있다. 이곳은 부산의 독특한 역사적 아픔을 체험할 수 있는 장소이다."),
    Attraction("동래읍성", "역사", "부산광역시 동래구 명륜, 복천, 칠산, 명장, 안락동 일대", "051-550-6634", "화~일 09:00 ~ 18:00", "동래읍성은 부산의 역사적 중심지로, 동래의 과거와 현재를 느낄 수 있는 곳이다. 성벽과 장대, 인생문 등에서 임진왜란 당시의 아픔과 평화로운 현재를 동시에 체험할 수 있다."),
    Attraction("유엔기념공원", "역사", "부산광역시 남구 유엔평화로 93", "051-625-0625", "09:00~17:00", "유엔기념공원은 한국전쟁 참전 유엔군 전사자들을 기리며, 그들의 희생을 기억하는 공간이다. 평화공원과 유엔군위령탑, 조각공원 등에서 전사자들의 이름과 희생을 추모하며 평화의 소중함을 되새길 수 있다."),
    Attraction("충렬사", "역사", "부산광역시 동래구 충렬대로 347", "0507-1416-4223", "09:00~18:00", "반듯하고 정갈한 분위기의 부산 충렬사, 뒤로는 망월산의 짙은 녹음이 충렬사를 감싸고 앞으로는 부산의 도심이 마주하고 있다. 본전까지 쭉 뻗어나간 대로를 따라 잘 정돈된 정원수와 예쁜 꽃들이 충렬사의 경건함을 전해준다. 조용히 묵념 한 후 뒤돌아서면 전통과 현대가 어우어진 멋진 풍광이 눈앞에 펼쳐진다."),
    Attraction("복천박물관", "역사", "부산광역시 동래구 복천로 63", "051-554-4263", "09:00 ~ 18:00", "복천동의 오래된 주택가 재개발 지역에서 그보다 훨씬 더 오래된 가야시대 무덤 40기가 발견되었다. 도굴의 흔적이 없는 완벽한 가야 왕국의 고분으로 금동관, 토기, 갑옷, 투구 등 수많은 유물이 출토되었다. 가야의 뛰어난 철기문화를 알려주는 유물과 다양한 무덤의 형태가 복천박물관에 전시되어 있다."),
    Attraction("소막마을", "역사", "부산광역시 남구 우암번영로 19", "없음", "없음", "우암동 소막마을은 일제강점기 일본의 소 수탈지였으며, 한국전쟁과 광복 후 피란민들의 거주지로 변모한 곳이다. 좁은 골목과 오래된 집들이 당시의 아픔을 간직하면서도 현재는 웃음과 따뜻한 분위기가 흐르는 마을이다."),
    Attraction("감천문화마을", "문화", "부산광역시 사하구 감내2로 203", "051-204-1444", "09:00 ~ 17:00", "감천문화마을은 한국전쟁 당시 피란민들이 산비탈을 개간해 만든 마을로, 2009년 마을미술프로젝트로 변화를 거쳐 부산의 대표 관광지로 자리 잡았다. 파스텔톤의 집들과 예술작품, 다양한 체험 프로그램이 이곳의 독특한 매력을 만들어낸다."),
    Attraction("해동용궁사", "문화", "부산광역시 기장군 기장읍 용궁길 86", "051-722-7744", "04:30 ~ 19:20", "기장에 위치한 해동용궁사는 바다와 산이 어우러진 아름다운 풍경을 자랑하는 사찰로, 해수관음대불과 바다를 배경으로 한 탁 트인 전망이 특징이다. 특히 해안산책로와 해돋이바위는 방문객들에게 잊을 수 없는 경치를 선사한다. 108계단을 오르며 소원을 비는 풍경도 인상적이다."),
    Attraction("호천마을", "문화", "부산광역시 부산진구 엄광로 491", "없음", "없음", "호천마을은 부산의 산복도로에 위치한 매력적인 마을로, 이 마을은 과거 호랑이가 자주 나타나던 곳으로 이름이 유래되었으며, 현재는 아기자기한 집들과 따뜻한 가로등, 그리고 아름다운 야경이 특징이다. 특히, 호천문화플랫폼과 멋진 산복도로 경치가 방문객들을 기다린다."),
    Attraction("죽성성당", "문화", "부산광역시 기장군 기장읍 죽성리 134-7", "없음", "없음", "기장의 죽성성당은 바다와 붉은 지붕이 어우러져 아름다운 풍경을 자랑하는 명소다. 드라마 *드림* 촬영지로 유명하며, 인기 있는 포토존과 해송이 독특한 매력을 더한다."),
    Attraction("국립해양박물관", "문화", "부산광역시 영도구 해양로301번길 45", "051-309-1900", "09:00~18:00", "국립해양박물관은 바다의 문화, 역사, 과학을 전시하는 종합해양박물관이다. 대형 수족관과 다양한 해양 체험 프로그램이 인기 있으며, 어린이박물관은 가족 단위 방문객에게 좋은 장소다."),
    Attraction("상해거리", "문화", "부산광역시 동구 중앙대로179번길 1", "없음", "없음", "상해거리는 부산의 차이나타운 특구로, 중국식 만두와 중식당 등이 인기 있는 명소다. 이곳은 이국적 분위기와 함께 부산의 근대 역사도 엿볼 수 있는 장소로, 매년 문화축제가 열린다."),
    Attraction("부산영화체험박물관, 트릭아이뮤지엄부산", "문화", "부산광역시 중구 대청로126번길 12", "0507-1377-4201 / 051-715-4200", "10:00 ~ 18:00", "부산영화체험박물관은 영화산업의 역사와 체험을 다양한 콘텐츠로 즐길 수 있는 공간으로, 최신 영상기법 체험과 촬영, 편집을 직접 해볼 수 있다. 이어서 트릭아이뮤지엄부산에서는 착시 효과를 활용한 신비로운 세계를 경험할 수 있다."),
    Attraction("민락수변공원", "공원", "부산광역시 수영구 민락동 110-19", "051-610-4742", "없음", "민락수변공원은 광안리 바다와 야경을 가까이에서 즐길 수 있는 명소로, 낮과 밤에 상반된 매력을 선보인다. 여름과 가을에는 많은 인파가 몰리고, 주변에는 먹거리와 카페가 있어 여유를 즐길 수 있다."),
    Attraction("용두산공원, 부산타워", "공원", "부산광역시 중구 용두산길 37-55", "051-860-7820 / 051-601-1800", "부산타워 10:00~22:00", "용두산공원은 부산의 대표 랜드마크로, 부산타워에서 부산항과 해운대 등 경치를 한눈에 볼 수 있다. 꽃시계와 시민의 종, 불꽃맵핑쇼 등 다양한 볼거리가 있으며, 최근 리뉴얼된 부산타워는 멋진 전망과 함께 AR체험도 제공한다."),
    Attraction("삼락생태공원", "공원", "부산광역시 사상구 삼락동 29-46", "051-303-0048", "없음", "삼락생태공원은 계절마다 다른 매력을 뽐내며, 벚꽃, 유채꽃, 연꽃, 코스모스 등 다양한 자연을 즐길 수 있다. 철새들이 휴식하는 겨울을 포함한 사계절의 아름다움을 경험하며 자연과 공생하는 방법을 배울 수 있다."),
    Attraction("부산시민공원", "공원", "부산광역시 부산진구 시민공원로 73", "051-850-6000", "05:00 - 24:00", "부산시민공원은 미군 하야리아 부대 부지에 조성된 공원으로, 백사장, 잔디광장, 뽀로로 도서관 등 다양한 시설을 갖춘 시민들의 쉼터다. 자연과 역사를 느낄 수 있는 공간으로, 아이들이 놀 수 있는 놀이시설과 맨발황톳길도 제공된다."),
    Attraction("중앙공원", "공원", "부산광역시 서구 망양로 193번길 187", "051-860-7800", "충혼탑 09:00 ~ 17:00", "옛 대청공원과 대신공원이 합쳐져 시민광장과 조각동산 등이 조성된 부산의 주요 공원이다. 4.19광장과 민주화운동 희생자를 추모하는 공간이 있다."),
    Attraction("민주공원", "공원", "부산광역시 중구 민주공원길 19", "051-790-7400", "09:00 ~ 18:00", "민주항쟁기념관을 중심으로 부산 시민의 민주주의 정신을 상징하는 곳으로, 4.19혁명과 부마민주항쟁 등 민주운동 역사를 기리며, 겹벚꽃이 만개하는 늦봄에 아름다움을 자랑한다."),
    Attraction("오랑대공원", "공원", "부산광역시 기장군 기장읍 기장해안로 340", "없음", "없음", "갯바위에 부딪히는 파도소리와 해안가 산책로를 따라 바다의 아름다움을 즐길 수 있는 곳이다. 밤에는 대변항의 야경도 감상할 수 있으며, 캠핑을 즐기는 사람들로도 유명하다. 특히 바다의 일출과 야경을 모두 감상할 수 있는 명소로, 용왕단에서 바라보는 일출 장관이 특징이다.")
]

# 카테고리 선택 옵션
categories = ["전체", "자연", "역사", "문화", "공원"]
selected_category = st.radio("카테고리를 선택하세요:", categories)

# 선택된 카테고리에 따라 명소 필터링
if selected_category and selected_category != "전체":
    filtered_Attractions = [r for r in Attractions if r.category == selected_category]
else:
    filtered_Attractions = Attractions

# 사용자 입력
query = st.text_input("원하는 명소를 알려주세요")

# 추천받기 버튼 클릭 시 로직
if st.button("추천받기"):
    if query.strip():
        with st.spinner("추천을 가져오는 중..."):
            related_Attractions = get_related_Attractions(query, filtered_Attractions, client)

        if related_Attractions:
            st.success(f"'{selected_category}' 카테고리에서 추천 명소를 찾았습니다!")

            for r in related_Attractions:
                st.markdown(f"### {r.name}")
                st.write(f"**주소:** {r.address}")
                st.write(f"**전화번호:** {r.phone}")
                st.write(f"**운영 시간:** {r.hours}")
                st.write(f"**설명:** {r.description}")
                st.write("")
                if r.name not in [res.name for res in st.session_state.selected_Attractions]:
                    st.session_state.selected_Attractions.append(r)
        else:
            st.warning("관련 명소를 찾을 수 없습니다.")
    else:
        st.error("키워드를 입력해주세요.")

if st.button("List 보기"):
        st.switch_page("pages/2_list.py")