from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

SERVICE_KEY = os.getenv("SERVICEKEY_ENV")

API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"


@app.route("/", methods=["GET", "POST"])
def index():
    drugs = []

    if request.method == "POST":
        keyword = request.form.get("keyword")

        params ={'serviceKey' : SERVICE_KEY,
         'pageNo' : '1',
         'numOfRows' : '5',
         'entpName' : '',
         'itemName' : '',
         'itemSeq' : '',
         'efcyQesitm' : keyword,
         'useMethodQesitm' : '',
         'atpnWarnQesitm' : '',
         'atpnQesitm' : '',
         'intrcQesitm' : '',
         'seQesitm' : '',
         'depositMethodQesitm' : '',
         'openDe' : '',
         'updateDe' : '',
         'type' : 'json' }

        try:
            response = requests.get(API_URL, params=params)
            data = response.json()

            items = (
                data.get("body", {})
                    .get("items", [])
            )

            drugs = items

        except Exception as e:
            print("에러:", e)

    return render_template("index.html", drugs=drugs)


if __name__ == "__main__":
    app.run(debug=True)
