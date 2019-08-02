from django import template

register = template.Library()

@register.filter(name='get_job_type')
def get_resource_type(value):
    if value == 1:
        return '运行'
    if value == '2':
        return '检查'

@register.filter(name='format_time')
def format_time(value):
    if value:
        date = value.split('T')[0]
        time = value.split('T')[1].split('.')[0]
        h_m_s = time.split(':')
        hour = int(h_m_s[0])+8
        minute = h_m_s[1]
        second = h_m_s[2]
        time = ':'.join([str(hour), minute ,second])
        return time
    else:
        return None
