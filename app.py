from flask import Flask, render_template, request, jsonify
import re
from collections import defaultdict
import requests
import os

app = Flask(__name__)

SERVICE_KEY = os.getenv("SERVICEKEY_ENV")

API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"


@app.route("/symptom", methods=["GET", "POST"])
def symptom():
    if request.method == "POST":
        user_input = request.json.get("text", "")

        results = predict_symptoms(user_input)

        print(user_input,results)
        
        return jsonify({
            "success": True,
            "symptoms": results
        })

    return render_template("symptom.html")

@app.route("/drug", methods=["GET", "POST"])
def index():

    drugs = []
    keyword = ""

    # symptom 페이지에서 넘어온 경우
    if request.method == "GET":
        keyword = request.args.get("symptom", "")

    # drug 페이지에서 직접 검색한 경우
    elif request.method == "POST":
        keyword = request.form.get("keyword", "")

    # 검색어가 있으면 API 호출
    if keyword:

        params = {
            'serviceKey': SERVICE_KEY,
            'pageNo': '1',
            'numOfRows': '5',
            'entpName': '',
            'itemName': '',
            'itemSeq': '',
            'efcyQesitm': keyword,
            'useMethodQesitm': '',
            'atpnWarnQesitm': '',
            'atpnQesitm': '',
            'intrcQesitm': '',
            'seQesitm': '',
            'depositMethodQesitm': '',
            'openDe': '',
            'updateDe': '',
            'type': 'json'
        }

        try:
            response = requests.get(API_URL, params=params)
            data = response.json()

            drugs = (
                data.get("body", {})
                    .get("items", [])
            )

        except Exception as e:
            print("에러:", e)

    return render_template(
        "index.html",
        drugs=drugs,
        keyword=keyword
    )




# 1. 입력 정규화 함수 (공백/특수문자 제거)
def normalize(text: str) -> str:
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", text)

# 2. symptom DB (이전에 만든 구조 그대로 사용)
symptom_db = {

    "통증": {
        "index": [
            "통증", "통",
            "아픔", "아프",
            "쑤심", "쑤시",
            "결림", "결리",
            "뻐근", "뻐근하",
            "찌릿", "찌릿하",
            "욱신", "욱신하",
            "화끈", "화끈하",
            "압통", "압",
            "저림", "저리"
        ],
        "items": [
            ["흉통", ["가슴", "통증"], ["가슴", "아픔"], ["가슴", "쑤심"], ["가슴", "찌릿"]],
            ["요통", ["허리", "통증"], ["허리", "아픔"], ["허리", "쑤심"], ["허리", "뻐근"]],
            ["경부통", ["목", "통증"], ["목", "아픔"], ["목", "결림"], ["목", "뻣뻣"]],
            ["견통", ["어깨", "통증"], ["어깨", "아픔"], ["어깨", "결림"], ["어깨", "뻐근"]],
            ["골반통", ["골반", "통증"], ["골반", "아픔"], ["엉덩이", "통증"]],
            ["사지통", ["팔", "통증"], ["다리", "통증"], ["팔다리", "아픔"], ["팔다리", "쑤심"]],
            ["신경통", ["찌릿"], ["전기", "오듯"]],
            ["압통", ["누르면", "아픔"], ["만지면", "아픔"]],
            ["작열감", ["화끈"], ["타는", "듯"]],
            ["방사통", ["통증", "퍼짐"], ["아픔", "퍼짐"]]
        ]
    },


    "호흡기": {
        "index": [
            "기침", "가래",
            "숨", "호흡",
            "쌕쌕", "천명",
            "목", "쉼", "쉰", "목소리",
            "인후", "통",
            "코", "막힘",
            "콧물",
            "재채기",
            "답답"
        ],
        "items": [
            ["객혈", ["피", "토"], ["피", "가래"], ["가래", "피"]],
            ["호흡곤란", ["숨", "막힘"]],
            ["천명", ["쌕쌕"]],
            ["흉부압박", ["가슴", "눌림"], ["가슴", "조임"]],
            ["가슴답답", ["가슴", "답답"]],
            ["잦은기침", ["기침", "잦은"]],
            ["마른기침", ["기침", "마른"]],
            ["야간기침", ["기침", "밤"]],
            ["목쉼", ["목", "쉰", "목소리"]],
            ["호흡시통증", ["호흡", "시", "통증"], ["숨", "쉴", "때", "아픔"], ["숨", "들이", "마실", "때", "아픔"]]
        ]
    },


    "소화기": {
        "index": [
            "배", "복부", "복",
            "위", "장",
            "속",
            "소화",
            "구토", "토",
            "설사",
            "변비",
            "메스꺼움",
            "신", "물",
            "속", "쓰림",
            "복", "통",
            "혈", "변",
            "흑", "변"
        ],
        "items": [
            ["복부팽만", ["배", "더부룩"], ["배", "빵빵"]],
            ["소화불량", ["소화", "안됨"]],
            ["복부불편", ["배", "불편"]],
            ["속쓰림", ["속", "쓰림"]],
            ["신물올라옴", ["신", "물"], ["위산", "역류"]],
            ["식욕부진", ["식욕", "없음"]],
            ["조기포만", ["조기", "포만"]],
            ["혈변", ["혈", "변"]],
            ["흑색변", ["흑", "변"]],
            ["삼킴곤란", ["삼킴", "곤란"]],
            ["구토", ["토"]],
            ["설사", ["설사"]],
            ["변비", ["변비"]]
        ]
    },


    "신경계": {
        "index": [
            "머리",
            "두", "통",
            "어지러움",
            "어지럼",
            "기절",
            "실신",
            "마비",
            "저림",
            "떨림",
            "경련",
            "기억",
            "의식",
            "말",
            "발음",
            "균형",
            "시야"
        ],
        "items": [
            ["두통", ["머리", "아픔"]],
            ["어지러움", ["어지러움"]],
            ["실신", ["정신", "잃음"]],
            ["의식저하", ["의식", "저하"]],
            ["기억력저하", ["기억", "저하"]],
            ["감각이상", ["감각", "이상"]],
            ["마비", ["움직임", "불가"]],
            ["떨림", ["손", "떨림"]],
            ["보행장애", ["걷기", "힘듦"]],
            ["균형감상실", ["균형", "상실"]],
            ["경련", ["근육", "경련"]],
            ["언어장애", ["말", "안", "나옴"]]
        ]
    },


    "근골격계": {
        "index": [
            "관절",
            "근육",
            "뼈",
            "팔",
            "다리",
            "무릎",
            "발목",
            "손목",
            "어깨",
            "허리",
            "목",
            "근력",
            "붓기"
        ],
        "items": [
            ["관절통", ["관절", "아픔"]],
            ["관절강직", ["관절", "뻣뻣"]],
            ["근육통", ["근육", "아픔"]],
            ["근력저하", ["힘", "없음"]],
            ["부종", ["붓기"]],
            ["운동범위감소", ["팔", "안", "올라감"]]
        ]
    },


    "비뇨기": {
        "index": [
            "소변", "오줌",
            "배뇨",
            "방광",
            "빈뇨",
            "혈뇨",
            "잔뇨",
            "요도"
        ],
        "items": [
            ["빈뇨", ["소변", "자주"]],
            ["배뇨통", ["소변", "볼", "때", "아픔"]],
            ["혈뇨", ["혈", "뇨"]],
            ["잔뇨감", ["잔뇨"]]
        ]
    },


    "전신증상": {
        "index": [
            "열", "발열",
            "오한",
            "몸살",
            "피로", "피곤",
            "권태",
            "무기력",
            "땀",
            "식은땀",
            "체중",
            "불면",
            "불안",
            "두근거림"
        ],
        "items": [
            ["탈수", ["입", "마름"]],
            ["체중감소", ["체중", "감소"]],
            ["체중증가", ["체중", "증가"]],
            ["발한", ["땀", "많이"]],
            ["야간발한", ["밤", "땀"]],
            ["피로감", ["피로"]],
            ["권태감", ["권태"]],
            ["불면", ["잠", "안", "옴"]],
            ["불안감", ["불안"]],
            ["심계항진", ["심장", "두근거림"]]
        ]
    },


    "피부": {
        "index": [
            "피부",
            "가려움",
            "간지러움",
            "발진",
            "붉은",
            "반점",
            "두드러기",
            "물집",
            "각질",
            "상처",
            "따가움"
        ],
        "items": [
            ["발진", ["피부", "발진"]],
            ["소양감", ["가려움"]],
            ["창백", ["혈색", "없음"]],
            ["황달", ["피부", "노래짐"], ["눈", "노래짐"]]
        ]
    },


    "안과": {
        "index": [
            "눈",
            "시야",
            "시력",
            "충혈",
            "눈곱",
            "침침",
            "흐림",
            "눈물",
            "가려움",
            "결막",
            "염"
        ],
        "items": [
            ["시야흐림", ["시야", "흐림"], ["앞", "흐림"]],
            ["복시", ["두개", "보임"]],
            ["충혈", ["눈", "빨개짐"]],
            ["결막염", ["결막", "염"]]
        ]
    },


    "이비인후과": {
        "index": [
            "귀",
            "코",
            "목",
            "이명",
            "난청",
            "청력",
            "콧물",
            "코막힘",
            "재채기",
            "인후",
            "통"
        ],
        "items": [
            ["이명", ["귀", "울림"]],
            ["난청", ["잘", "안", "들림"]],
            ["귀먹먹", ["귀", "먹먹"]]
        ]
    }
}


def predict_symptoms(user_input: str, top_k: int = 5):
    text = normalize(user_input)

    scores = defaultdict(int)
    evidence = {}

    # 1️⃣ 계통 순회
    for system, data in symptom_db.items():

        index_keywords = data["index"]
        items = data["items"]

        # 2️⃣ 계통 매칭 (index 기반)
        system_match = any(
            normalize(k) in text for k in index_keywords
        )

        # 계통이 전혀 안 맞으면 스킵
        if not system_match:
            continue

        # 3️⃣ 실제 증상 매칭
        for group in items:
            for keyword in group:
                nk = normalize(keyword)

                if nk and nk in text:
                    key = (system, group[0])
                    scores[key] += 1
                    evidence[key] = keyword

    # 4️⃣ 정렬
    sorted_results = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 5️⃣ 결과 출력
    output = []
    for (system, symptom), score in sorted_results[:top_k]:
        output.append({
            "계통": system,
            "의심증상": symptom,
            "근거": evidence[(system, symptom)],
            "점수": score
        })

    return output


if __name__ == "__main__":
    app.run(debug=True)
