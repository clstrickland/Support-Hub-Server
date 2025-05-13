import azure.functions as func
import azure.durable_functions as df
import jwt
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO  # Import BytesIO
import os  # Import the os module
from requests_toolbelt.multipart import decoder
import base64
import json

ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID")
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID")

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    client = df.DurableOrchestrationClient(starter)
    # 1. Get and validate JWT
    auth_header = req.headers.get("Authorization")
    """
    So, Microsoft Entra ID bearer tokens are not normal JWTs. They can be decoded like normal JWTs, but they cannot be verified like normal JWTs.
    It is kinda explained here: https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/issues/609#issuecomment-1915423345
    The workaround is to use an Azure API Management service to validate the token, check the claims, and pass the claims to the function.
    """
    # userUpn = req.headers.get("X-User-UPN", "joeaggie@tamu.edu")
    # userHash = req.headers.get("X-Auth-Hash", "1234")
    # if not userUpn or not userHash:
    #     return func.HttpResponse("Authorization header is missing.", status_code=401)

    try:
        token = auth_header.split(" ")[1]
        # --- Fetch Microsoft's JWKS ---
        # jwks_uri = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/discovery/v2.0/keys?appid={ENTRA_CLIENT_ID}" #Common endpoint
        # jwks_client = jwt.PyJWKClient(jwks_uri)
        # signing_key = jwks_client.get_signing_key_from_jwt(token)
        # --- Decode and validate the JWT ---
        decoded_token: dict = jwt.decode(
            token,
            # signing_key,
            verify=False, # we can't verify an access token because it isn't a proper JWT
            options={"verify_signature": False},
            algorithms=["RS256"],
            require=["exp", "iss", "aud", "scp", "upn"],
            audience=f"api://{ENTRA_CLIENT_ID}",  # Replace with your Entra App Client ID
            issuer=f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/v2.0", #Get tenant ID and create issuer.
        )
        logging.info(f"Decoded token: {decoded_token}")
        userUpn = decoded_token.get("upn")
        if not userUpn:
          return func.HttpResponse("upn claim is missing from token.", status_code=400)

        # --- Hash the JWT ---
        userHash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expiration_time = datetime.now(timezone.utc) + timedelta(days=1)
        # expiration_time = datetime.fromtimestamp(decoded_token.get("exp"))
        expiration_str = expiration_time.isoformat() + "Z"
    except jwt.exceptions.PyJWTError as e:
        logging.error(f"JWT validation error: {e}")
        return func.HttpResponse(f"Invalid token. {e}", status_code=401)
    except Exception as ex:
        logging.error(f"Token processing error: {ex}")
        return func.HttpResponse(f"Error processing token. {ex}", status_code=400)

    # 2. Parse multipart/form-data

    try:
        fields = {}
        files = {}

        content_type_header = req.headers.get('content-type')
        if not content_type_header:
            raise ValueError('Content-Type header is missing')

        multipart_data = decoder.MultipartDecoder(req.get_body(), content_type_header)

        for part in multipart_data.parts:
            content_disposition = part.headers.get(b'Content-Disposition').decode('utf-8')
            if 'filename' in content_disposition:
                name = content_disposition.split('name=')[1].split(';')[0].strip('"')
                files[name] = BytesIO(part.content)
            else:
                name = content_disposition.split('name=')[1].strip('"')
                fields[name] = part.text

        title = fields.get("title")
        description = fields.get("description")
        image_data = files.get("image")  # This will be a BytesIO object or None

        if not title or not description:
            return func.HttpResponse("Missing required fields: title and description.", status_code=400)

    except Exception as e:
        logging.error(f"Multipart parsing error: {e}")
        return func.HttpResponse(f"Error parsing form data: {e}", status_code=400)

    expiration_time = datetime.now(timezone.utc) + timedelta(days=1)
    # expiration_time = datetime.fromtimestamp(decoded_token.get("exp"))
    expiration_str = expiration_time.isoformat() + "Z"


    # 3. Start the orchestrator
    orchestrator_input = {
        "token_hash": userHash,
        "expiration_str": expiration_str,
        "title": title,
        "description": description,
        "upn": userUpn,
        "image_data": base64.b64encode(image_data.read()).decode('utf-8') if image_data else None,  # Read the image data (if present)
    }
    # orchestrator_input = {
    #     "token_hash": token_hash,
    #     "expiration_str": expiration_str,
    #     "title": title,
    #     "description": description,
    #     "upn": preferred_username,
    #     "image_data": base64.b64encode(image_data.read()).decode('utf-8') if image_data else None,  # Read the image data (if present)
    # }
    instance_id = await client.start_new("ticket_orchestrator", None, orchestrator_input)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    # return (json.dumps(orchestrator_input))

    return json.dumps({"instance_id": instance_id})