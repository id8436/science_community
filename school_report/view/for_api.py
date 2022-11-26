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

class SchoolTimetableApi:
    # 클래스변수 설정.
    params = {
        "KEY": "11182151c14d43c481a878c5b8d7cd82",  # 발급받은 키.
        "Type": "json",
    }
    def __init__(self, ATPT_OFCDC_SC_CODE='K10', SD_SCHUL_CODE='7821011', GRADE=2, CLASS_NM=3, school_name='원주중학교'):
        self.params = {}
        middle_school = True  # 추후 학교구분기능 넣기.
        if middle_school:
            self.base_url = "https://open.neis.go.kr/hub/misTimetable"  # 중학교인 경우.
            self.max_perio = 7
        # 시간설정.
        today = datetime.datetime.today()
        day_num = datetime.timedelta(days=today.weekday() + 1)
        sunday = today - day_num
        a_day = datetime.timedelta(days=1)
        last_day = sunday + 7 * a_day
        from_date = sunday.strftime('%Y%m%d')
        to_date = last_day.strftime('%Y%m%d')
        self.schoolinfo = {
            "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE, # 시도교육청 코드.
            "SD_SCHUL_CODE": SD_SCHUL_CODE,  # 학교코드
            "TI_FROM_YMD": from_date,  # 시작일.(포함)
            "TI_TO_YMD": to_date,  # 끝일.(포함)
            "GRADE": GRADE,  # 학년
            "CLASS_NM": CLASS_NM,  # 반
        }
    def get_data(self):
        URL = self.base_url
        self.params.update(SchoolTimetableApi.params)
        self.params.update(self.schoolinfo)
        response = requests.get(URL, params=self.params)
        try:
            j_response = json.loads(response.text)['misTimetable']  # 정보 키는 이것 하나 뿐.
            return j_response[1]["row"]
        except:
            return None  # 데이터가 없음.

    def create_list(self):
        base_info = self.get_data()
        base_dict = {}
        for i in range(self.max_perio):
            base_dict[i + 1] = []
        perio = 0
        for time in base_info:
            perio = perio % self.max_perio  # 교시
            perio += 1
            i_date = time['ALL_TI_YMD']  # 오늘의 날짜.
            i_subject = time['ITRT_CNTNT']  # 글자 앞에 -가 들어가 있어 이건 빼준다.
            if i_subject[0] == '-':  # 어째서인지 일반 과목 앞에 -가 붙는다.
                i_subject = i_subject[1:]
            i_time = int(time['PERIO'])  # 교시 인덱스
            if perio != i_time:  # 교시 인덱스가 다르다면...(최대시간을 안채웠는데 다음날짜로.)
                if perio == i_time + 1:  # 영어회화 같이 교사가 2명 들어가는 경우, 동일한 정보가 2번 연속 나온다.
                    base_dict[i_time][-1] += '(특수)'  # 방금 넣었던 것에 대하여 표기
                    perio -= 1  # 이 사이클을 다시 돌리기 위해서.
                    continue
                for j in range(self.max_perio - perio+1):  # 남은 시간 채우기.
                    base_dict[perio].append('-')
                    perio += 1
                perio = 1
            base_dict[perio].append(i_subject)

        return base_dict