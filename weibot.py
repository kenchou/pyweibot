#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Ken Chou <kenchou77@gmail.com>'

import weibo
import argparse
import os
import pickle
import json


# 回调地址，可以用这个默认地址
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'


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


def get_code(weibo_client):
    referer_url = weibo_client.get_authorize_url()
    print 'open this authorize url: %s' % referer_url

    code = raw_input('copy and paste the code:')
    return code


# ----------------
# parse args
parser = argparse.ArgumentParser()
parser.add_argument('message', nargs='?',                       help='message to post to weibo.com')
parser.add_argument('-c', '--config',  nargs='?', default=None, help='config of weibo.com')
parser.add_argument('-f', '--file',    nargs='?', default=None, help='picture file to post to weibo.com')
parser.add_argument('-a', '--at',      nargs='?', default="",   help='extra notify @someone')
parser.add_argument('-v', '--verbose', action='count',          help='verbosity')

args = parser.parse_args()

# load config
config = get_config(args.config if args.config else 'weibo.json')
APP_KEY = config['APP_KEY']
APP_SECRET = config['APP_SECRET']

message = args.message if args.message else raw_input()
message = "%s %s" % (message, args.at)
picture_file = args.file

token_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], '_token')

weibo_client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

token = get_token(token_file=token_file, weibo_client=weibo_client)
weibo_client.set_access_token(token.access_token, token.expires_in)

if picture_file:
    # 发图片微博
    f = open(picture_file, 'rb')
    r = weibo_client.statuses.upload.post(status=message, pic=f)
    f.close()  # APIClient不会自动关闭文件，需要手动关闭
else:
    # 发普通微博
    weibo_client.statuses.update.post(status=message)
