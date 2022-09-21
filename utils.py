from datetime import datetime
import requests as req
import json
from typing import Iterable, Any, Tuple


with open('config.json') as f:
    CONFIG = json.load(f)

def log_print(text, type='info'):
    print('[' + datetime.now().strftime("%H:%M:%S") + '] ' + text)

def tg_api(method, parameters, token=CONFIG['tg_token'], file=None):
    url = 'https://api.telegram.org/bot' + token + '/' + method
    headers = {}

    if file == None:
        r = req.post(url, params=parameters, headers=headers).json()
    else:
        r = req.post(url, params=parameters, headers=headers, files={'file': file}).json()
    
    if not r['ok']:
        log_print('TG ERROR #{}: "{}"'.format(r['error_code'],
                                                r['description']))
                                                        #r['parameters']))
        return None

    return r['result']

def signal_first(it:Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    iterable = iter(it)
    yield True, next(iterable)
    for val in iterable:
        yield False, val

def signal_last(it:Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    iterable = iter(it)
    ret_var = next(iterable)
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var

    