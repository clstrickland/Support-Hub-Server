import azure.functions as func
import requests
import logging
import os  # Import the os module
import base64
if os.environ.get("LOCAL_DEMO_MODE") == "true":
    LOCAL_DEMO_MODE = True
    import random
    
async def submit_attachment_activity(inputData: tuple) -> None:
    ticket_id, image_data = inputData
    image_data = base64.b64decode(image_data.encode())
    # dummy_endpoint = os.environ.get("DUMMY_ENDPOINT", "https://httpbin.org/post") #Use httpbin as default.

    # # Simulate a dummy API call.
    # try:
    #     files = {'file': ('image.jpg', image_data, 'image/jpeg')}
    #     response = requests.post(
    #         f"{dummy_endpoint}",  # Replace with your actual attachment endpoint
    #         data={"ticket_id": ticket_id},
    #         files=files,
    #         timeout=10
    #     )

    #     response.raise_for_status()
    # except requests.exceptions.RequestException as e:
    #     logging.error(f"Error submitting attachment: {e}")
    #     raise # Re-raise to fail the activity

    file_path = os.path.join(os.getcwd(), f"{ticket_id}_image.jpg")

    try:
        # Save the image to the current working directory
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)
        logging.info(f"Image saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving attachment: {e}")
        raise # Re-raise to fail the activity