import json
from py1337x import py1337x
from hurry.filesize import size, si

torrents = py1337x(proxy='1337x.to', cache='cache', cacheTime=5000)

def search1337(query):
    torrentResults = torrents.search(query, sortBy='seeders', order='desc')
    print(torrentResults["items"][:5])
    return torrentResults

#def getMagnetJSON(query):
#    magnetLink = search1337(torrents.info(torrentId=query['items'][0]['torrentId'])['magnetLink'])
#    print(magnetLink)
#    print(size(10000))

t = search1337("fire walk with me")
x = 0
for item in t["items"]:
    print(f"name: ", {item["name"]}, "seeders: ", {item["seeders"]}, "size: ", {item["size"]})

