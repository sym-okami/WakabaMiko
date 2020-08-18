import miko
import json

if __name__ == "__main__":
    auth = None
    with open("./bot_auth.json") as f:
        auth = json.load(f)

    wakaba = miko.Miko(auth["user"], auth["oauth"])
    for channel in auth["channels"]:
        wakaba.join(channel, verbose=True)
    wakaba.listen()