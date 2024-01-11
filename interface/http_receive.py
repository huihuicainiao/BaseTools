# -*-coding:utf-8 -*-
# Author: Zenghui Tang
# Date: 2023/3/13
# Time: 10:21
import json
import argparse
from flask import Flask, request
from flask import jsonify
app = Flask(__name__)


@app.route('/algorithm/detectResult', methods=['POST'])
def pl_det_start():
    data = json.loads(request.get_data())
    print(data)
    return jsonify({})


def argv_parse():
    parser = argparse.ArgumentParser(usage="it's usage tip.", description="wp_dl detect app.")
    parser.add_argument("--port", type=int, default=3007, help="app port.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="web host.")
    return parser.parse_args()


if __name__ == "__main__":
    argv = argv_parse()
    print("argv:", argv)
    app.run(debug=True, port=argv.port, host=argv.host)
