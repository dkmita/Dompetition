#!/usr/bin/env python
import os, Cookie
import facebook
import facebookLogin

print """Content-Type: text/html\n
Set-Cookie: session=12345; path=/; domain=i72.182.111.191; version=1\n"""
print "<!DOCTYPE html><html><body>"

apple_key = os.environ['APPLE_KEY']
print facebookLogin.facebookLoginHtml % locals()
if "HTTP_COOKIE" in os.environ:
    fb_cookie_str = os.environ["HTTP_COOKIE"] 
    simple_cookie = Cookie.SimpleCookie()
    simple_cookie.load(fb_cookie_str)
    
    fb_cookie = facebook.get_user_from_cookie(simple_cookie,os.environ["APPLE_KEY"],"a71e6b82bb35f955956255effdb40b1b")
    if fb_cookie:
        print str(fb_cookie) + "<br />"
        graph = facebook.GraphAPI(fb_cookie["access_token"])
        profile = graph.get_object("me")
        
        print profile, "<br />"
        print profile["first_name"], profile["last_name"], profile["email"]
    else:
        print "No fb cookie"
    print 
else:
    print "HTTP_COOKIE not set!"
print "</body></html>"

