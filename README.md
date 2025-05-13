# Support Hub Server

This project is the server-side implementation for the [**Support Hub Client**](https://github.com/clstrickland/Support-Hub-Client), a Windows application designed for managed devices. The client allows users to submit support tickets directly from the system tray. This server handles ticket creation requests, authenticates users, and processes ticket submissions.

## Features

- **Ticket Submission**: Receives ticket creation requests from the Support Hub Client.
- **User Authentication**: Authenticates users via JSON Web Tokens (JWT). (Note: Ideally, this should be handled by Azure API Management for better security and compliance.)
- **Durable Functions**: Implements Azure Durable Functions for orchestrating workflows.
- **Customizable Ticketing System Integration**: The ticket creation logic is left unimplemented to allow integration with various ticketing systems.
- **File Attachments**: Supports optional file attachments for tickets.

## Architecture

This project uses Azure Functions and Durable Functions to manage workflows. The key components include:

- **HTTP Triggers**:
  - `SubmitTicketHttpTrigger`: Handles ticket submission requests.
  - `StatusHttpTrigger`: Allows clients to check the status of submitted tickets.
- **Orchestrator**:
  - `ticket_orchestrator`: Coordinates the ticket submission process, including token validation, ticket creation, and file attachment handling.
- **Activity Functions**:
  - `submit_ticket_activity`: Handles the logic for creating a ticket.
  - `submit_attachment_activity`: Processes and stores file attachments.
- **Entity Function**:
  - `ExchangedTokenEntity`: Tracks the state of tokens to prevent reuse.

## Prerequisites

- Python 3.8 or later
- Azure Functions Core Tools
- Azure CLI
- Virtual environment for Python dependencies

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/clstrickland/Support-Hub-Server
   cd azure-functions-durable-python-master/samples/support-hub-server
    ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file and set the following variables:

   ```bash
   ENTRA_CLIENT_ID=<your-client-id>
   ENTRA_TENANT_ID=<your-tenant-id>
   LOCAL_DEMO_MODE=true  # Set to true for local testing
   ```

5. **Run the Functions Locally**:

   ```bash
   func start
   ```
