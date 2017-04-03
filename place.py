import urllib
import urllib2
import time
import json
import random
from PIL import Image

user_agent_list=list(set([ua for ua in urllib.urlopen("https://raw.githubusercontent.com/sqlmapproject/sqlmap/master/txt/user-agents.txt").read().splitlines() if not ua.startswith("#")]))

accounts = []
sessions = {}

#set ur reddit accounts here
accounts.append("username:password")
accounts.append("username:password")
accounts.append("username:password")

#set which picture you want to put in to the r/place
#the color of all pixels in this picture must belong to this 16 colors.even one bit of differences will result in ignored
picpre = Image.open('tusk.png')

#offset is the position of the top-left pixel
offsetx = 234
offsety = 341

col = {0:(255,255,255),1:(228,228,228),2:(136,136,136),3:(34,34,34),4:(225,167,209),5:(229,0,0),6:(229,149,0),7:(160,106,66),8:(229,217,0),9:(184,224,68),10:(2,190,1),11:(0,211,221),12:(0,131,199),13:(0,0,234),14:(207,110,228),15:(130,0,128)}
inv_col = {v: k for k, v in col.iteritems()}


opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', random.choice(user_agent_list))]
for account in accounts:
    username = account.split(":")[0]
    password = account.split(":")[1]
    data = urllib.urlencode({'op': 'login-main', 'user': username, 'passwd': password, 'api_type': 'json'})
    resp = opener.open('https://www.reddit.com/api/login/'+urllib.quote(username), data).read()
    sessions[username] = json.loads(resp)["json"]["data"]["cookie"]

pic = picpre.convert('RGB')

while True:
    for session in sessions.keys():
        cookie = sessions[session]
        done = False
        xtest=0
        while xtest<pic.width and done == False:
            ytest = 0
            while ytest<pic.height and done == False:
                resp = opener.open("https://www.reddit.com/api/place/pixel.json?x="+str(xtest+offsetx)+"&y="+str(ytest+offsety)).read()
                color = json.loads(resp)["color"]
                if(pic.getpixel((xtest,ytest)) == col.get(color)):
                    print xtest+offsetx,ytest+offsety,"is good"
                else:
                    print xtest+offsetx,ytest+offsety,"need change"

                    write_color = inv_col.get(pic.getpixel((xtest,ytest)))
                    data = urllib.urlencode({'x': xtest + offsetx, 'y': ytest + offsety, 'color': write_color})
                    newopener = urllib2.build_opener()
                    newopener.addheaders = [('User-Agent', random.choice(user_agent_list))]
                    newopener.addheaders.append(('Cookie', 'reddit_session=' + cookie))
                    modhash = json.loads(newopener.open("https://reddit.com/api/me.json").read())["data"]["modhash"]
                    newopener.addheaders.append(('x-modhash', modhash))
                    next = newopener.open("https://www.reddit.com/api/place/draw.json", data).read()
                    print next
                    finalresp = newopener.open(
                        "https://www.reddit.com/api/place/pixel.json?x=" + str(xtest+offsetx) + "&y=" + str(ytest+offsety)).read()
                    if session in finalresp:
                        print "Added successfully"
                        done = True
                    else:
                        print finalresp
                ytest = ytest + 1
            xtest = xtest + 1
    time.sleep(330)
