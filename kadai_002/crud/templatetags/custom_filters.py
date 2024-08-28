from django import template

register = template.Library()

@register.filter(name='weekday_name')
def weekday_name(closed_days):
    print(closed_days)  
    weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    return ", ".join([weekdays[day] for day in closed_days])
