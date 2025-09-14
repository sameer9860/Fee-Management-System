from django import template

register = template.Library()


@register.filter
def only_school_name(school_code):
    """
    eg. DSN-1991 -> DSN,  logic: [DSN, 1991][0] -> DSN
    """
    school_short_name = school_code.split("-")[0]
    return school_short_name
