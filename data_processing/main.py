from flask_restplus import Resource, Api, fields
from flask import Flask, request, jsonify
from flask_restplus import reqparse
from googlenews import process_headlines
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
interaction_model = api.model(
    "interaction",
    {
        "language": fields.String("language of the article we want to fetch"),
        "country": fields.String("unicode of the country we want to fetch"),
    },
)


@api.route("/get_headlines")
class GetTree(Resource):
    endpoint_arguments = reqparse.RequestParser()
    endpoint_arguments.add_argument("language", type=str, required=True)
    endpoint_arguments.add_argument("country", type=str, required=True)

    @api.expect(endpoint_arguments)
    def get(self):
        language = request.args.get("language")
        country = request.args.get("country")
        return process_headlines()


@api.route("/healthcheck")
class GetHealthCheck(Resource):
    """
    Endpoint to return healthcheck response ok.
    """

    def get(self):
        return {"msg": "ok"}, 200


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


# Access swaggger documentation at http://<address>:5000/
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
