import string

def fixEmail(email):
    if email[0] == '"':
        return str.lower(email[1:-1])
    else:
        return str.lower(email)
