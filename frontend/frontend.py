from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from datetime import datetime
import json
from usr_profile_lib.usr_profile_log import UserProfileLogger

app = Flask(__name__)
UserProfileLogger.USER_PROFILE_DB = "/var/usr_prf/user_profile.db"

es = Elasticsearch("elastic.haochen.lu", port="9200")
#es = Elasticsearch("localhost:9200", port="9200")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log/click", methods=["POST"])
def log():
    data = request.get_json()
    # log into db
    timestamp = datetime.now()
    return "Ok"

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data["query"]
    results_size = data["results_size"]
    results_from = data["results_from"]
    email = data["email"]

    # log the user query
    with UserProfileLogger(email) as profile_logger:
        profile_logger.log_search(
            query=query, query_type="Unknown", ranking_type=None)

    q = {
        "query": {
            "multi_match" : {
                "query" : query,
                "fields" : [ "title", "text"]
            }
        },
        "from": results_from,
        "size": results_size
    }
    el_res = es.search(body=q)
    res = {"results": []}
    res["n_results"] = el_res["hits"]["total"]
    for pe in el_res["hits"]["hits"]:
        obj = {}
        obj["id"] = pe["_id"]
        obj["string"] = pe["_source"]["title"]
        obj["url"] = "http://en.wikipedia.org/wiki/" + pe["_source"]["title"]
        obj["synopsys"] = pe["_source"]["text"][:400]
        res["results"].append(obj)

    return json.dumps(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
