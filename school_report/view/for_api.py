import requests
import json
import datetime

class SchoolMealsApi:
    # 클래스변수 설정.
    base_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": "11182151c14d43c481a878c5b8d7cd82",  # 발급받은 키.
        "Type": "json",
    }
    def __init__(self, ATPT_OFCDC_SC_CODE='K10', SD_SCHUL_CODE='7821011'):
        self.params = {}
        today = datetime.datetime.now()
        from_date = str(today.year) + str(today.month) + str(today.day)
        today += datetime.timedelta(days=7)
        to_date = str(today.year) + str(today.month) + str(today.day)
        self.schoolinfo = {
            "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE, # 시도교육청 코드.
            "SD_SCHUL_CODE": SD_SCHUL_CODE,  # 학교코드
            "MLSV_FROM_YMD": from_date,  # 급식 시작일.(포함)
            "MLSV_TO_YMD": to_date  # 급식 끝일.(포함)
        }
    def get_data(self):
        URL = SchoolMealsApi.base_url
        self.params.update(SchoolMealsApi.params)
        self.params.update(self.schoolinfo)
        response = requests.get(URL, params=self.params)
        try:
            j_response = json.loads(response.text)['mealServiceDietInfo']  # 정보 키는 이것 하나 뿐.
            if j_response[0]["head"][0]["list_total_count"] == 1:  # 들어온 급식의 갯수.(휴일 제외하고 들어온다.)
                return j_response[1]["row"][0]
            else:
                return j_response[1]["row"]
        except:
            return None  # 데이터가 없음.