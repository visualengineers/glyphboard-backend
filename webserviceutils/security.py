from functools import wraps
from flask import request

ALLOWED_EXTENSIONS = set(['zip', 'csv'])
API_ALLOWED_IPS = 0

def init(allowed_ips):
    global API_ALLOWED_IPS
    API_ALLOWED_IPS = allowed_ips

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getrequestip(req):
    if req.headers.getlist("X-Forwarded-For"):
        requestip = req.headers.getlist("X-Forwarded-For")[0]
    else:
        requestip = req.remote_addr
    return requestip

def ipcheck(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if API_ALLOWED_IPS is None:
            return f(*args, **kwargs)
        req_ip = getrequestip(request)
        for IP in API_ALLOWED_IPS:
            if str(req_ip).startswith(IP) or str(req_ip) == IP:
                return f(*args, **kwargs)
        return 'Your IP Is Not allowed ' + req_ip
    return wrapped
