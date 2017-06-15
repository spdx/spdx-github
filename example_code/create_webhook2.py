import requests

#a simple API request that requires authentication
r = requests.get('https://api.github.com/user', auth=('abuhman',
                                                      'abuhmanspassword'))
#response is 200 ok
print r

#I try a post request to create a webhook on the repo abuhman/test_webhooks,
#which I am an admin of.  I am able to create a webhook on this repository
#using the web page, but not the API request below.
r = requests.post('https://github.com/abuhman/test_webhooks/hooks',
                   data = '{"name":"web","active": true,'
                   '"events": ["pull_request"],"config": '
                   '{"url": "http://abuhmans.localhost/",'
                   '"content_type":"json"}}',
                   auth=('abuhman', 'abuhmanspassword'))
#response is 403 forbidden
print r
