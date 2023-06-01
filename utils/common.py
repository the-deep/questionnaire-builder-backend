from user_agents import parse


def to_camelcase(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_type(request):
    http_agent = request.META.get('HTTP_USER_AGENT')
    if http_agent:
        user_agent = parse(http_agent)
        return user_agent.browser.family + ',' + user_agent.os.family
    return
