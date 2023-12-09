from custom_account.models import Debt, Point

def payment(user, amount, cause):
     points = Point.objects.filter(user=user)
     total_point = 0  # 총 포인트 담을 변수.
     for point in points:
         total_point += point.amount

     if amount > total_point:  # 값을 수 있는 포인트가 없다면..
         debt = Debt.objects.create(user=user, amount=amount, debt_cause=cause)
     else:
         paid = Point.objects.create(user=user, amount=amount, transaction_detail=cause, payment_method='내부소모')

     return True  # 성공했음을 반환.