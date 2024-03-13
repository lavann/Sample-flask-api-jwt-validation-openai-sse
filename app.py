
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from functools import wraps
import jwt_validator
from custom_auth_handler import AuthHandler
import openai_completions as open_ai_streaming_completions

# MSAL Configuration Expires 30/04/2024
app = Flask(__name__)
CORS(app, resources={r"/endpoint*": {"origins": "https://api.some-domain.net"}})

decoded_token  = None

# Error handler


@app.errorhandler(AuthHandler)
def handle_auth_error(e):
    """
    Error handler for AuthError exceptions.
    """
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response



def get_auth_token_header() -> str:
        token = request.args.get('Authorization')  # Get the token from the query string
        bearer_token = f"bearer {token}"
        if not bearer_token:
            return jsonify({"error": "No token provided"}), 401

        parts = bearer_token.split()
        if parts[0].lower() != "bearer":
            raise AuthHandler({"code": "invalid_header",
                            "description":
                                "Authorization header must start with"
                                " Bearer"}, 401)
        elif len(parts) == 1:
            raise AuthHandler({"code": "invalid_header",
                            "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise AuthHandler({"code": "invalid_header",
                            "description":
                                "Authorization header must be"
                                " Bearer token"}, 401)
        
        token = parts[1]  # Remove 'Bearer ' from token
        return token



def validate_jwt_request_(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_auth_token_header()
        decoded_token = jwt_validator.validate_jwt(token)
        return f(decoded_token,*args, **kwargs)
    
    return decorator







@app.route('/openai', methods=['get'])
@validate_jwt_request_
def send_message(token: str):
    """ Endpoint to receive user messages and start streaming responses. """
    user_message = request.args.get("message")
    
    #I can do more stuff with the token should I wish to. Right now, I don't need to
    #The validator is checking for the scope and audience of the token
    #This is there in future to enable more functionality via authz for specific users
    # Ensure message is not empty
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    return Response(open_ai_streaming_completions.generate_streaming_response(user_message), content_type='text/event-stream')


#health check endpoint
@app.route('/health', methods=['get'])
def health_check():
    return jsonify({"status": "healthy"})



if __name__ == '__main__':
    app.register_error_handler(AuthHandler, handle_auth_error)
    app.run()
