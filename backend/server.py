import os
from livekit import api
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins": "*"}})

@app.route("/getToken")
async def getToken():
    name = request.args.get("name", "my name")
    room = request.args.get("room", None)

    if not room:
        room = await generate_room_name()
    #1.35.27

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
