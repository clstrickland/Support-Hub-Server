import azure.functions as func
import requests
import logging
import os  # Import the os module
if os.environ.get("LOCAL_DEMO_MODE") == "true":
    LOCAL_DEMO_MODE = True
    import random

async def submit_ticket_activity(inputData: tuple) -> str:
    title, description, upn = inputData
    # dummy_endpoint = os.environ.get("DUMMY_ENDPOINT", "https://httpbin.org/post") #Use httpbin as default.

    # # Simulate a dummy API call
    # try:
    #     response = requests.post(
    #         f"{dummy_endpoint}",  # Replace with your actual endpoint
    #         json={"title": title, "description": description, "upn": upn},
    #         timeout=10
    #     )
    #     response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    #     # Assuming the dummy endpoint returns the ticket ID
    #     return response.json().get("json").get("upn") #Grab the UPN to simulate return data.

    # except requests.exceptions.RequestException as e:
    #     logging.error(f"Error submitting ticket: {e}")
    #     raise  # Re-raise to fail the activity

    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"UPN: {upn}")
    if LOCAL_DEMO_MODE:
        fake_ticket_id = str(random.randint(100000, 999999))
        return fake_ticket_id
    else:
        return "123456789"  # Return a dummy ticket ID