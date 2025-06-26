from datetime import datetime

def calculate_age(birthdate):
    today = datetime.today()
    birth = datetime.strptime(birthdate, '%Y-%m-%d')
    age = today.year-birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age = age - 1
    
    return age

def convert_currency(amount, rate=1330):
    return amount*rate


def calculate_bmi(height, weight):
    height_m = height/100
    bmi = weight/(height_m**2)
    return round(bmi, 2)


if __name__=='__main__':
    print(calculate_age('2000-01-01'))
    print(convert_currency(100000))
    print(calculate_bmi(188, 50))