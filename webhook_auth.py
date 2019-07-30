import redis, os, sys, secrets, requests
from functions.hashing.hashing import *
from flask import request, Flask, json, jsonify
from parse_it import ParseIt


# the variables below will only be used by the requester API
print("reading config variables")
parser = ParseIt()
redis_host = parser.read_configuration_variable("redis_host")
redis_port = parser.read_configuration_variable("redis_port")
receiver_webhook_url = parser.read_configuration_variable("receiver_webhook_url")
requester_webhook_url = parser.read_configuration_variable("requester_webhook_url")

# create flask app
app = Flask(__name__)

# if a redis is configured this must be an example requester API so connect to it
if redis_port is not None and redis_host is not None:
    r = redis.Redis(host=redis_host, port=redis_port, db=0)


# the receiver endpoint - this is the api2api endpoint that will be contacted by the requester api
@app.route('/receiver', methods=["GET"])
def receiver():
    # check the request authorization header and get the hashed value and webhook address from it
    auth_header = request.headers['Authorization']
    auth_type, auth_url, auth_hashed_token = auth_header.split(" ")
    # callback to the webhook of the sender in the authorization header with the hashed value in the body & the url of
    # itself
    payload = json.dumps({"hash": auth_hashed_token, "url": receiver_webhook_url})
    headers = {'Content-Type': "application/json"}
    response = requests.request("POST", auth_url, data=payload, headers=headers)
    # check that the response from the callback is HTTP status 200
    if response.status_code == 200:
        # if the unhashed token is in fact the same as the hashed one
        if check_secret_matches(response.text, auth_hashed_token):
            # if the hash and unhashed are of the same key it works and return a good reply
            return jsonify({"allowed": True}), 200
        # otherwise return 401 and a message that it blocked the attempt
        else:
            return jsonify({"allowed": False}), 401
    # otherwise return 401 and a message that it blocked the attempt
    else:
        return jsonify({"allowed": False}), 401


# the webhook endpoint - this is the api2api endpoint that the receiver endpoint will use to authenticate the request
# against
@app.route('/webhook', methods=["POST"])
def webhook():
    # find the unhashed value and delete it from the backend db
    request_dict = request.json
    unhashed = r.get(request_dict["hash"])
    r.delete(request_dict["hash"])
    # find the requested url that the hash was sent to and delete it from the backend db
    requested_url = r.get(request_dict["hash"] + "_url")
    r.delete(request_dict["hash"] + "_url")
    # if it's in the db return it and the requested url is the same one as the one the request was sent to originally
    if (unhashed is not None) and (requested_url.decode('utf-8') == request.json["url"]):
        return unhashed.decode('utf-8'), 200
    # otherwise return not allowed
    else:
        return jsonify({"allowed": False}), 401


# the example endpoint - this is the endpoint a user will contact to check the auth works\doesn't works as part of the
# example POC
@app.route('/example', methods=["GET"])
def example():
    # create a random unhashed one time use pass and a hash of it
    unhashed_token = secrets.token_urlsafe()
    hashed_token = hash_secret(unhashed_token)
    # setex the it into the DB with 600 seconds ttl
    r.setex(hashed_token, 600, unhashed_token)
    # setex the url that the hash is going to be sent to into the DB with 600 seconds ttl
    r.setex(hashed_token + "_url", 600, receiver_webhook_url)
    # send the request to the receiver API
    payload = ""
    headers = {'Authorization': "Webhook " + requester_webhook_url + " " + hashed_token}
    response = requests.request("GET", receiver_webhook_url, data=payload, headers=headers)
    # display the result you got back from the receiver endpoint
    return jsonify(response.json()), response.status_code


# used for when running with the 'ENV' envvar set to dev to open a new thread with flask builtin web server
def run_dev(dev_host='0.0.0.0', dev_port=5000, dev_threaded=True):
    try:
        app.run(host=dev_host, port=dev_port, threaded=dev_threaded)
    except Exception as e:
        print("Flask connection failure - dropping container")
        print(e, file=sys.stderr)
        os._exit(2)


# will usually run in gunicorn but for debugging set the "ENV" envvar to "dev" to run from flask built in web server
if os.getenv("ENV", "prod") == "dev":
    try:
        run_dev()
    except Exception as e:
        print("Flask connection failure - dropping container")
        print(e, file=sys.stderr)
        os._exit(2)
