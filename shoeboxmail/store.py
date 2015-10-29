emails = []
_next_id = 1

def get_all():
    return emails

def find(msg_id):
    msg_id = int(msg_id)
    for msg in emails:
        if msg['id'] == msg_id:
            return msg
    return None

def add(msg):
    global emails, _next_id
    msg['id'] = _next_id
    _next_id += 1
    emails.append(msg)

def delete_all():
    global emails
    emails = []
    _next_id = 1

def delete_msg(msg_id):
    global emails
    msg_id = int(msg_id)
    for i, email in enumerate(emails):
        if email['id'] == msg_id:
            del emails[i]
            break
