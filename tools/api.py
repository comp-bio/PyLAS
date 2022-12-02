from flask import jsonify, request, Flask, make_response


def bcov(file, start=0, default=None):
    with open(file, 'rb') as f:
        f.seek(start * 2)
        while True:
            v = f.read(2)
            if not v or len(v) == 0:
                yield default
                continue
            yield v[0] * 256 + v[1]


def compress(sig, K=16):
    return [int(sum(sig[i:i+K])/K) for i in range(0, len(sig), K)]


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


app = Flask(__name__, static_url_path='', static_folder='')


# --------------------------------------------------------------------------- #
@app.route('/depth/<string:sample>', methods=['POST', 'OPTIONS'])
def depth(sample):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    results = []
    if len(request.json) > 0:
        for v in request.json:
            ch, l, r = (v[0], int(v[1]) - 1, int(v[2]))
            bc = bcov(f"{sample}/{ch}.bcov", l, 0)
            cv = [next(bc) for i in range(r - l)]
            results.append(compress(cv))
            # results.append(cv)
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9950)
