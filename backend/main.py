from flask_restplus import Resource, Api, fields
from flask import Flask, request, jsonify
from flask_restplus import reqparse
from utility import get_recommendations_with_article
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
interaction_model = api.model(
    "interaction",
    {
        "language": fields.String("language of the articles"),
        "country": fields.String("country of originine of the article"),
    },
)


@api.route("/get_tree")
class GetTree(Resource):
    endpoint_arguments = reqparse.RequestParser()
    endpoint_arguments.add_argument("language", type=str, required=True)
    endpoint_arguments.add_argument("country", type=str, required=True)

    @api.expect(endpoint_arguments)
    def get(self):
        return get_recommendations_with_article(
            request.args.get("language"), request.args.get("country")
        )


@api.route("/post_interaction_data")
class PostInteractionData(Resource):
    """
    Endpoint to send the user interactions with the entities on the widget to logs/storage.
    Each click/interaction with an entity will call this endpoint as post request containing
    interaction_model type of json. This json will be printed/saved to logs/databse and it will
    return null to the post request.
    """

    @api.expect(interaction_model)
    def post(self):
        new_interaction = api.payload
        print(new_interaction, flush=True)
        return


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
    app.run(host="0.0.0.0", port=5000, debug=True)
