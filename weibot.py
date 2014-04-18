#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ken Chou <kenchou77@gmail.com>'

import weibo
import urllib
import urllib2
import argparse
import os
import pickle
import json


APP_KEY = '235133751'  # 你申请的APP_KEY
APP_SECRET = 'b05603e088a5e9409881c6f4e7a1cfdc'  # 你申请的APP_SECRET
# 回调地址，可以用这个默认地址
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
USER_ID = 'kenchou77@gmail.com'  # 微博账号
PASSWORD = 'Tgg6RLzm'  # 微博密码

def get_config(config_file='weibot.json'):
    f = open(config_file)
    config = json.load(f)
    f.close()
    return config

def get_token(token_file='_token', weibo_client=None):
    try:
        f = open(token_file)
        token = pickle.load(f)
        f.close()
    except IOError:
        # token does not exist
        code = get_code(weibo_client)
        token = weibo_client.request_access_token(code)

        f = open(token_file, 'w+')
        pickle.dump(token, f)
        f.close()

    return token


#模拟授权并且获取回调地址上的code，以获得acces token和token过期的UNIX时间
def get_code(weibo_client):
    referer_url = weibo_client.get_authorize_url()
    print 'open this authorize url: %s' % referer_url

    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)

    post_data = {
        'client_id': APP_KEY,
        'redirect_uri': CALLBACK_URL,
        'userId': USER_ID,
        'passwd': PASSWORD,
        'isLoginSina': '0',
        'action': 'submit',
        'response_type': 'code',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Host': 'api.weibo.com',
        'Referer': referer_url
    }

    req = urllib2.Request(url=AUTH_URL, data=urllib.urlencode(post_data), headers=headers)
    resp = urllib2.urlopen(req)

    # print 'callback url is : %s' % resp.geturl()
    code = resp.geturl()[-32:]

    # code = raw_input('copy and paste the code:')

    # print 'code is : %s' % resp.geturl()[-32:]
    return code

# ----------------
# parse args
parser = argparse.ArgumentParser()
parser.add_argument('message', nargs='?',                       help='message to post to weibo.com')
parser.add_argument('--file',    '-f', nargs='?', default=None, help='picture file to post to weibo.com')
parser.add_argument('--at',      '-a', nargs='?', default="",   help='extra notify @someone')
parser.add_argument('--verbose', '-v', action='count',          help='verbosity')

args = parser.parse_args()

message = args.message if args.message else raw_input()
message = "%s %s" % (message, args.at)
picture_file = args.file

token_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], '_token')

weibo_client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

token = get_token(token_file=token_file, weibo_client=weibo_client)
# 新浪返回的token，类似abc123xyz456
# print client.token
weibo_client.set_access_token(token.access_token, token.expires_in)

if picture_file:
    # 发图片微博
    f = open(picture_file, 'rb')
    r = weibo_client.statuses.upload.post(status=message, pic=f)
    f.close()  # APIClient不会自动关闭文件，需要手动关闭
else:
    # 发普通微博
    weibo_client.statuses.update.post(status=message)
