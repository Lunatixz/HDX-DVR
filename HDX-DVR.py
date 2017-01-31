import os
import urllib
import requests
import string
from hashlib import md5, sha1
import json
import subprocess
import time
import shlex

name = "HDX DVR"
os.environ['TZ'] = 'US/Eastern'
time.tzset()
print("Time zone set to: "+time.tzname)

class InvalidToken(Exception):
    """The Schedules Direct server returned an invalid token.  The server could be down or blocked by a firewall.  If not try again in 30 minutes."""

class SchedulesDirect(object):
    def __init__(self,username,password,hdhomerun=None):
        global config
        login = {'username':username,'password':sha1(password.encode()).hexdigest()}
        r = requests.post('https://json.schedulesdirect.org/20141201/token',json=login)
        self.authToken=r.json()['token']
        if self.authToken=="CAFEDEADBEEFCAFEDEADBEEFCAFEDEADBEEFCAFE":
            raise InvalidToken
        self.tokenExp=time.time()+86400
        if not config['lineupURI']:
            config.update({'lineupURI':self.match(hdhomerun)['uri']})
        self.URI=config['lineupURI']

    def match(self, hdhomerun=None):
        if hdhomerun:
            possibleLineup=requests.post("https://json.schedulesdirect.org/20141201/map/lineup/", data=hdhomerun.getLineup(),headers={'token':self.authToken}).json()
            if possibleLineup.items()[0] == 100:
                self.SDlineup= possibleLineup.keys()[0]
                print("Match Found!")
                return self.SDlineup
            else:
                if len(possibleLineup<5):
                    for i in possibleLineup:
                        if "Y" or "y" in str(input("Is this lineup correct? [Y/n] ")):
                            self.SDlineup = i
                            return i
                    print("No automatch found.  Matching manually.")
                    return self.manualMatch()
        return self.manualMatch()
    def manualMatch(self):
        global config
        headends=requests.get('https://json.schedulesdirect.org/20141201/headends',params={'country':input("What is your country? "),'postalcode':input("What is your ZIP Code? ") if not config['zip'] else config['zip']},headers={'token':self.authToken})
        print('\n\n')
        num=0
        lineups=list()
        for he in headends:
            for lineup in he['lineups']:
                lineups.append(lineup)
                num+=1
                print(str(num)+'.  '+lineup['name'])
        lineupnum=int(input('Select a lineup 0 through '+str(num)+'.  '))-1
        return lineups[lineupnum]




class HDHR(object):
    def __init__(self):
        """

        :rtype: object
        """
        self.deviceInfo = self.getTuners
        self.IP = self.deviceInfo['LocalIP']
        self.tunerCount = json.loads(urllib.request.urlopen('http://' + str(self.IP) + '/discover.json').read().decode("utf-8"))['TunerCount']
        self.channelsByName = {channel['GuideName']: {"URL":channel['URL'],"GuideNumber":channel['GuideNumber']} for channel in self.getLineup()}

    def getLineup(self):
        with urllib.request.urlopen(self.deviceInfo['LineupURL']).read().decode("utf-8") as lineupjson:
            return json.loads(lineupjson)

    def getTuners(self):
        with urllib.request.urlopen('http://ipv4.my.hdhomerun.com/discover').read().decode("utf-8") as discoverjson:
            return json.loads(discoverjson)[0]
    def getURLbyChannelNum(self,channelnum):

    def record(self, duration, channel):
        subprocess.Popen(shlex.split('wget '+self.getURLbyChannelNum(channel)))



class recorder(object):
    def __init__(self,  HDHomeRun):
        self.recordings = list()
        self.HDrun=HDHomeRun
        self.
    def newRecording(self, channel, start_time, end_time):
        if type(start_time) == string:
            if "PM" in start_time:
                for c in start_time
        recording = (int(channel),start_time, end_time - start_time)
        self.recordings = self.recordings + recording

progDir=os.path.dirname(__file__)
os.chdir(progDir)
if os._exists('dvr.cfg'):
    with open('dvr.cfg', 'r') as configf:
        dvrConfig = json.load(configf)

else:
    config = {}
    print("It seems this is your first time using {0}.  Beginning setup.").format(name)
    config.update({"zip":input("Please input your 5 digit zipcode: "),"username":input("SchedulesDirect Username: "),"password":input("SchedulesDirect Password: ")})
    with open("dvr.cfg",'w+') as configf:
        configf.write(json.dumps(config))
    os.mkdir('Recordings')
    saveDir=os.path.join(progDir,'Recordings')
