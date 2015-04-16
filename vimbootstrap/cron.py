#!/usr/bin/env python
# encoding: utf-8
import json
import urllib3
from google.appengine.api import memcache


class Requests(object):

    http = urllib3.PoolManager()

    def get(self, url):
        response = self.http.request('GET', url)
        return {"data": response.data,
                "status": response.status,
                "json": json.loads(response.data)}

requests = Requests()

URL = "http://vimawesome.com/api/plugins"


def w_json(plugin_list, update=True, finish=False):
    if type(plugin_list) == list:
        text = ",".join([json.dumps(p) for p in plugin_list])
        if not finish:
            text += ", "
    else:
        text = plugin_list

    with open('./awesomevim.json', (update) and "a" or "wb") as f:
        f.write(text)


def main():
    result = requests.get(URL)
    if result["status"] == 200:
        j = result["json"]
        w_json("[", update=False)
        w_json(j.get("plugins"))
        max_page = j.get("total_pages")
        for i in range(2, max_page + 1):
            loop_result = requests.get(URL + "?page=" + str(i))
            loop_j = loop_result["json"].get("plugins")
            if i == max_page:
                w_json(loop_j, finsh=True)
            else:
                w_json(loop_j)
        w_json("]")

        memcache.add('awesomevim',
                     json.loads(open("./awesomevim.json").read()),
                     324000)


if __name__ == "__main__":
    main()
