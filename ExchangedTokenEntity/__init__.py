import azure.functions as func
from datetime import datetime, timezone
import azure.durable_functions as df


# class ExchangedTokenEntity:
#     def __init__(self):
#         self.state = {"used": False, "expiration": None}

#     def set_used(self, expiration_str):
#         self.state["used"] = True
#         self.state["expiration"] = expiration_str  # Store as ISO string

#     def is_used(self):
#         if self.state["used"]:
#             return True
#         return False
    
#     def to_dict(self):
#         return self.state

#     def from_dict(self, state_dict):
#         self.state = state_dict


def entity_function(context: df.DurableEntityContext):
    state = context.get_state(lambda: {"used": False, "expiration": None})
    operation_name = context.operation_name

    if operation_name == "set_used":
        expiration_str = context.get_input()
        state["used"] = True
        state["expiration"] = expiration_str  # Store as ISO string
    elif operation_name == "is_used":
        result = state["used"]
        context.set_result(result)

    context.set_state(state)


main = df.Entity.create(entity_function)