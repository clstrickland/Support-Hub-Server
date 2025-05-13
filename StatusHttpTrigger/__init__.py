import azure.functions as func
import azure.durable_functions as df
import logging
import json
import jwt
import os
import hashlib
from datetime import datetime, timedelta, timezone

ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID")
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID")

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to check status processed a request.')
    client = df.DurableOrchestrationClient(starter)

    # 1. Get and validate JWT
    auth_header = req.headers.get("Authorization")
    # userUpn = req.headers.get("X-User-UPN", "joeaggie@tamu.edu")
    # userHash = req.headers.get("X-Auth-Hash", "1234")
    # if not userUpn or not userHash:
    #     return func.HttpResponse("Authorization header is missing.", status_code=401)

    try:
        token = auth_header.split(" ")[1]
        # --- Hash the JWT ---
        user_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    except Exception as ex:
        logging.error(f"Token processing error: {ex}")
        return func.HttpResponse(f"Error processing token. {ex}", status_code=400)


    

    instance_id = req.params.get('instance_id')
    # user_hash = req.headers.get("X-Auth-Hash", "1234")

    if not instance_id or not user_hash:
        return func.HttpResponse("Missing instance_id or X-Auth-Hash header.", status_code=400)

    # Fetch the status of the orchestration instance
    status = await client.get_status(instance_id)

    if not status:
        return func.HttpResponse("Instance not found.", status_code=404)

    # Check if the user hash matches
    # logging.info(f"Custom status: {json.dumps(status.custom_status, indent=2)}")
    # if status.custom_status and status.custom_status.get("token_hash") == None:
    #     # not ready for polling yet, return blank response
    #     return func.HttpResponse(json.dumps({"instance_id": status.instance_id}), status_code=200, mimetype="application/json")

    if status.custom_status and status.custom_status.get("token_hash") != user_hash:
        logging.error(f"Unauthorized access to instance {instance_id}.\nExpected: {status.custom_status.get('token_hash')}\nActual: {user_hash}")
        return func.HttpResponse("Unauthorized access.", status_code=401)

    logging.info(f"Current Status: {type(status.to_json()['runtimeStatus'])}")


    # Return the status
    response_data = {
        "instance_id": status.instance_id,
        # "runtime_status": status.runtime_status,
        # "input": status._input,
        # "output": status.output,
        "created_time": status.created_time.isoformat(),
        "last_updated_time": status.last_updated_time.isoformat(),
        "runtimeStatus": status.to_json()['runtimeStatus'],
        # "custom_status": status.custom_status,
    }

    response_data.update(status.output or {})


    if (status.custom_status is not None and (ticket_id := status.custom_status.get("ticket_id"))):
        response_data["ticket_id"] = ticket_id

    return func.HttpResponse(json.dumps(response_data), status_code=200, mimetype="application/json")