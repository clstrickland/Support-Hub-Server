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

## API Management Service Implementation

To enhance security and compliance, it is recommended to use an Azure API Management service to handle authentication and route requests to the Azure Function. Below is an example of how to configure the API Management service:

1. **Create an API Management Service**:
   Use the Azure Portal or CLI to create an API Management service. Ensure that only the API Management service can send requests to the Azure Function.

2. **Add a Policy for Request Validation**:
   Add the following policy to the API Management service to validate incoming requests, extract attributes, and pass them to the Azure Function:

   ```xml
   <policies>
       <inbound>
           <base />
           <validate-azure-ad-token tenant-id="<your-tenant-id>" header-name="Authorization" failed-validation-httpcode="401" failed-validation-error-message="Authorization Validation Failed" output-token-variable-name="user_jwt">
               <client-application-ids>
                   <application-id><your-client-application-id></application-id>
               </client-application-ids>
               <required-claims>
                   <claim name="scp" match="any" separator=" ">
                       <value>Tickets.Submit</value>
                   </claim>
               </required-claims>
           </validate-azure-ad-token>
           <set-variable name="upn" value="@(context.Variables.GetValueOrDefault<Jwt>("user_jwt").Claims.GetValueOrDefault("upn", ""))" />
           <set-variable name="issuanceTime" value="@(context.Variables.GetValueOrDefault<Jwt>("user_jwt").IssuedAt.ToString())" />
           <choose>
               <when condition="@(context.Variables.ContainsKey("upn") && context.Variables["upn"] != "" && context.Variables.ContainsKey("issuanceTime") && context.Variables["issuanceTime"] != null)">
                   <set-variable name="authHash" value="@{
                       using (SHA256 sha256Hash = SHA256.Create())
                       {
                           string input = context.Variables.GetValueOrDefault<string>("upn") + ":" + context.Variables.GetValueOrDefault<string>("issuanceTime");
                           byte[] bytes = Encoding.UTF8.GetBytes(input);
                           byte[] hash = sha256Hash.ComputeHash(bytes);
                           return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
                       }
                   }" />
                   <set-header name="X-User-UPN" exists-action="override">
                       <value>@(context.Variables.GetValueOrDefault<string>("upn"))</value>
                   </set-header>
                   <set-header name="X-Auth-Hash" exists-action="override">
                       <value>@(context.Variables.GetValueOrDefault<string>("authHash"))</value>
                   </set-header>
               </when>
               <otherwise>
                   <return-response>
                       <set-status code="400" reason="UPN Claim Missing" />
                       <set-body>The required UPN claim is missing from the JWT token.</set-body>
                   </return-response>
               </otherwise>
           </choose>
           <authentication-managed-identity resource="<your-managed-identity-resource-id>" />
       </inbound>
       <backend>
           <base />
       </backend>
       <outbound>
           <base />
       </outbound>
       <on-error>
           <base />
       </on-error>
   </policies>
   ```

3. **Replace Placeholders**:
   - `<your-tenant-id>`: Replace with your Azure AD tenant ID.
   - `<your-client-application-id>`: Replace with the client application ID.
   - `<your-managed-identity-resource-id>`: Replace with the resource ID of the managed identity.

This configuration ensures that only authenticated and authorized requests are processed by the Azure Function.
