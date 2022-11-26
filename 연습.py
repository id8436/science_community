import requests
import json
import datetime

from school_report.view.for_api import SchoolTimetableApi

max_perio = 7
base_list = []
for i in range(max_perio):
    base_list.append([i+1])
print(base_list)
print(base_list[3])
info = SchoolTimetableApi()
base_info = info.create_list()

#
# perio = 0
# for time in base_info:
#     perio = perio % max_perio  # 교시
#     i_date = time['ALL_TI_YMD']  # 오늘의 날짜.
#     i_subject = time['ITRT_CNTNT']  # 글자 앞에 -가 들어가 있어 이건 빼준다.
#     if i_subject[0] == '-':  # 어째서인지 일반 과목 앞에 -가 붙는다.
#         i_subject = i_subject[1:]
#     i_time = int(time['PERIO']) - 1  # 교시 인덱스
#     if perio != i_time:  # 교시 인덱스가 다르다면...(최대시간을 안채웠는데 다음날짜로.)
#         if perio == i_time+1:  # 영어회화 같이 교사가 2명 들어가는 경우, 동일한 정보가 2번 연속 나온다.
#             base_list[i_time][-1] += '(특수)'  # 방금 넣었던 것에 대하여 표기
#             continue
#         for j in range(max_perio-perio):  # 남은 시간 채우기.
#             base_list[perio].append('-')
#             perio += 1
#         perio = 0
#
#     base_list[perio].append(i_subject)
#     perio += 1

print(base_info)