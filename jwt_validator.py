import jwt #PyJWT library, a Python library to work with JSON Web Tokens (JWT).
from cryptography.hazmat.backends import default_backend #he default_backend is a reference to the default cryptographic backend used for cryptographic operations (such as encryption, decryption, signing, and verification) which abstracts away details about the specific cryptographic libraries or implementations being used under the hood
from cryptography.hazmat.primitives import serialization #serialization  to convert keys (both public and private) into a standardized format (e.g., PEM or DER
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers #numbers that make up an RSA public key, specifically the modulus (n) and the public exponent (e).
import base64
import requests
from custom_auth_handler import AuthHandler

#from dotenv import load_dotenv
import os

# Load the environment variables from .env.local file
#load_dotenv(dotenv_path='.env.local')

# Load the environment variables from .env.local file
ISSUER = os.getenv('ISSUER')
AUDIENCE = os.getenv('AUDIENCE')
JWKS_URI = os.getenv('JWKS_URI')


# Function to decode the Base64-URL encoded strings
def base64url_decode(input):
    rem = len(input) % 4
    if rem > 0:
        input += '=' * (4 - rem)
    return base64.urlsafe_b64decode(input)

#function that fetches the public key from the JWKS and returns the matched key if found from the bearer token
def fetch_public_key(unverified_header):
    response = requests.get(JWKS_URI)  # Fetch the public key from the well known configuration
    jwks = response.json()

    kid = unverified_header["kid"]  # Get the kid from the unverified header

    matched_key = [x for x in jwks['keys'] if x['kid'] == kid]  # Find the key in the JWKS with the matching kid
    if matched_key:
        matched_key = matched_key[0]
        #public_key = RSAAlgorithm.from_jwk(json.dumps(matched_key))  # Create a public key object from the matched key
        return matched_key
    else:
        raise AuthHandler({"code": "Key Not Found",
                        "description":
                            "No key found matching the kid in the JWKS"}, 401)

#function that gets the unverified header from the bearer token
def get_unverified_header(bearer_token):
    try:
        return jwt.get_unverified_header(bearer_token)
    # If the token is in an invalid format, raise an error
    except jwt.DecodeError:
        raise AuthHandler({"code": "invalid_header",
                        "description":
                            "Unable to parse authentication"
                            " token."}, 401)

#function that validates the bearer token
def validate_jwt(token):    
    unverified_header = get_unverified_header(token)
    match_key = fetch_public_key(unverified_header)
    n = match_key["n"]
    e = match_key["e"]

    # Decode the base64url encoded strings
    n_decoded = base64url_decode(n)
    e_decoded = base64url_decode(e)
    
    
    #convert the JWK to a public key
    n_int = int.from_bytes(n_decoded, byteorder='big')
    e_int = int.from_bytes(e_decoded, byteorder='big')
    public_key = RSAPublicNumbers(e=e_int, n=n_int).public_key(default_backend())

    #convert to PEM format
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)  

    #verify the JWT
    try:
        decoded = jwt.decode(token, pem, algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER, options={"verify_signature": True})        

    
    except jwt.ExpiredSignatureError:
                raise AuthHandler({"code": "token_expired",
                                "description": "token is expired"}, 401)
    except jwt.InvalidAudienceError:
        raise AuthHandler({"code": "invalid_claims",
                        "description":
                            "incorrect claims,"
                            "please check the audience and issuer"}, 401)
    except jwt.InvalidIssuerError:
        raise AuthHandler({"code": "invalid_claims",
                        "description":
                            "incorrect issuer,"
                            "please check the audience and issuer"}, 401)
    except Exception:
        raise AuthHandler({"code": "invalid_header",
                        "description":
                            "Unable to parse authentication"
                            " token."}, 401)
    return decoded