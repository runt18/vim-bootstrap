#!/usr/bin/env python
# encoding: utf-8
import json
import requests


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
    if result.status_code == 200:
        j = result.json()
        w_json("[", update=False)
        w_json(j.get("plugins"))
        max_page = j.get("total_pages")
        for i in range(2, max_page + 1):
            loop_result = requests.get(URL + "?page=" + str(i))
            loop_j = loop_result.json().get("plugins")

            if i == max_page:
                w_json(loop_j, finish=True)
            else:
                w_json(loop_j)
            print i
        w_json("]")


if __name__ == "__main__":
    main()
