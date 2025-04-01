import requests
import json
import datetime

class SchoolMealsApi:
    base_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    # 필수 키.
    params = {
        "KEY": "d45bdc00d66a4b2985a5fbeecfc2e0e4",  # 발급받은 키.
        "Type": "json",
        "pindex":1,

    }
    def __init__(self, show_days=5, ATPT_OFCDC_SC_CODE='K10', SD_SCHUL_CODE='7801101'):
        self.params = SchoolMealsApi.params.copy()  # 위의 클래스 변수 복사
        today = datetime.datetime.now()
        from_date = today.strftime('%Y%m%d')
        target_day = today + datetime.timedelta(days=show_days)
        to_date = target_day.strftime('%Y%m%d')

        self.schoolinfo = {
            "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,  # 시도교육청 코드
            "SD_SCHUL_CODE": SD_SCHUL_CODE,  # 학교코드
            "MLSV_FROM_YMD": from_date,  # 급식 시작일
            "MLSV_TO_YMD": to_date,  # 급식 끝일
            "pSize":show_days*3,  # 100까지 가능.(5일치를 불러온다면 조식, 중식, 석식 15이 되어야 함.)
        }

    def get_data(self):
        URL = SchoolMealsApi.base_url
        self.params.update(self.schoolinfo)
        try:
            response = requests.get(URL, params=self.params, verify=False)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            data = response.json()
            meal_info = data.get("mealServiceDietInfo", [])

            if not meal_info:
                return None  # 데이터 없음

            total_count = meal_info[0]["head"][0].get("list_total_count", 0)
            return meal_info[1]["row"] if total_count > 1 else meal_info[1]["row"][0]
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            print(f"오류 발생: {e}")
            return None


class SchoolTimetableApi:
    params = {
        "KEY": "11182151c14d43c481a878c5b8d7cd82",  # 발급받은 키.
        "Type": "json",
    }

    def __init__(self, ATPT_OFCDC_SC_CODE='K10', SD_SCHUL_CODE='7821011', GRADE=2, CLASS_NM=3):
        self.params = SchoolTimetableApi.params.copy()  # 클래스 변수 복사
        self.base_url = "https://open.neis.go.kr/hub/misTimetable"
        self.max_perio = 7

        today = datetime.datetime.today()
        sunday = today - datetime.timedelta(days=today.weekday())  # 이번 주 일요일
        next_saturday = sunday + datetime.timedelta(days=6)  # 이번 주 토요일

        from_date = sunday.strftime('%Y%m%d')
        to_date = next_saturday.strftime('%Y%m%d')

        self.schoolinfo = {
            "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,  # 시도교육청 코드
            "SD_SCHUL_CODE": SD_SCHUL_CODE,  # 학교코드
            "TI_FROM_YMD": from_date,  # 시작일
            "TI_TO_YMD": to_date,  # 끝일
            "GRADE": GRADE,  # 학년
            "CLASS_NM": CLASS_NM,  # 반
        }

    def get_data(self):
        URL = self.base_url
        self.params.update(self.schoolinfo)
        try:
            response = requests.get(URL, params=self.params)
            response.raise_for_status()
            data = response.json()
            return data.get("misTimetable", [{}])[1].get("row", None)
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            print(f"오류 발생: {e}")
            return None

    def create_list(self):
        base_info = self.get_data()
        if base_info is None:
            return None

        base_dict = {i + 1: [] for i in range(self.max_perio)}

        for time in base_info:
            perio = int(time.get('PERIO', 0))  # 교시
            i_subject = time.get('ITRT_CNTNT', '').lstrip('-')  # 과목명 정리
            base_dict[perio].append(i_subject)

        return base_dict


if __name__ == '__main__':
    meal_api = SchoolMealsApi()
    print(meal_api.get_data())
