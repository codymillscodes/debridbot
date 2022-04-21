import json
from py1337x import py1337x

torrents = py1337x(proxy='1337x.to', cache='cache', cacheTime=5000)
torrentResults = torrents.search('no way home', sortBy='seeders', order='desc')
#print(torrentResults)
#print(torrents.info(torrentId=torrentResults['items'][0]['torrentId'])['magnetLink'])
#torrentId = 
magnetLink = torrents.info(torrentId=torrentResults['items'][0]['torrentId'])['magnetLink']
print(magnetLink)