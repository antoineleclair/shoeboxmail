emails = []
_next_id = 1

def add(msg):
    global emails, _next_id
    msg['id'] = _next_id
    _next_id += 1
    emails.append(msg)
