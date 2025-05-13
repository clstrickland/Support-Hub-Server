import azure.durable_functions as df
import logging
import json

def ticket_orchestrator(context: df.DurableOrchestrationContext):
    input_data = context.get_input()
    token_hash = input_data["token_hash"]
    expiration_str = input_data["expiration_str"]
    title = input_data["title"]
    description = input_data["description"]
    upn = input_data["upn"]
    image_data = input_data.get("image_data")  # Optional

    current_status = context.custom_status or {}
    current_status.update({"token_hash": token_hash})
    context.set_custom_status(current_status)

    logging.info(json.dumps(context.custom_status, indent=2))
    logging.info(f"Storing token hash: {token_hash} for instance {context.instance_id}")

    # 1. Check if token has been exchanged
    entity_id = df.EntityId("ExchangedTokenEntity", token_hash)
    is_used = yield context.call_entity(entity_id, "is_used")
    # is_used = False

    if is_used:
        return {"status": "error", "message": "Token has already been exchanged."}

    # 2. Mark token as used
    yield context.call_entity(entity_id, "set_used", expiration_str)

    # 3. Submit ticket
    ticket_id = yield context.call_activity("submit_ticket_activity", (title, description, upn))

    current_status = context.custom_status or {}
    current_status.update({"ticket_id": ticket_id})
    context.set_custom_status(current_status)

    # 4. Submit attachment (if image exists)
    if image_data and ticket_id:
        yield context.call_activity("submit_attachment_activity", (ticket_id, image_data))

    return {"status": "success"}

main = df.Orchestrator.create(ticket_orchestrator)