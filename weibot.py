#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'kzhang'

import weibo
import urllib
import urllib2



APP_KEY = '235133751' #你申请的APP_KEY
APP_SECRET = 'b05603e088a5e9409881c6f4e7a1cfdc' #你申请的APP_SECRET
#回调地址，可以用这个默认地址
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
USER_ID = 'kenchou77@gmail.com' #微博账号
PASSWORD = 'Tgg6RLzm' #微博密码


#模拟授权并且获取回调地址上的code，以获得acces token和token过期的UNIX时间
def get_code():

    client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    referer_url = client.get_authorize_url()
    print "authorize url is : %s" % referer_url

    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)

    post_data = {
        "client_id": APP_KEY,
        "redirect_uri": CALLBACK_URL,
        "userId": USER_ID,
        "passwd": PASSWORD,
        "isLoginSina": "0",
        "action": "submit",
        "response_type": "code",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0",
        "Host": "api.weibo.com",
        "Referer": referer_url
    }

    req = urllib2.Request(url=AUTH_URL, data=urllib.urlencode(post_data), headers=headers)
    try:
        resp = urllib2.urlopen(req)

        print "callback url is : %s" % resp.geturl()
        code = resp.geturl()[-32:]

        print "code is : %s" % resp.geturl()[-32:]
    except Exception, e:
        print e
    return code


def begin():

    client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

    code = get_code()

    r = client.request_access_token(code)
    print r
    access_token = r.access_token # 新浪返回的token，类似abc123xyz456
    expires_in = r.expires_in # token过期的UNIX时间

    client.set_access_token(access_token, expires_in)

    #发普通微博
    client.statuses.update.post(status=u'测试 aaa 23333')

    #发图片微博
    # f = open('C:/pic/test.jpg', 'rb')
    # r = client.statuses.upload.post(status=u'测试OAuth 2.0带图片发微博', pic=f)
    # f.close() # APIClient不会自动关闭文件，需要手动关闭

begin()
