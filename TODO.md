1. fix function use with groq
1.5. add setmax back
2. status bar for cx -i
    a. provider, model, chat, history on/off, history max, context use,
3. model per chat? /chat.global on/off, if on, use global model, if off, use chat specific provider/model ?? plan this out better


100. per command help. yawn


socket refactor ideas:

● Here's how I'd structure a cleaner socket protocol refactor:

  1. Unified Message Format

  // Single message envelope for all communication
  struct Message {
      type: MessageType,
      id: Option<String>,        // For request/response correlation
      payload: serde_json::Value, // Structured data
      metadata: HashMap<String, String>, // Headers, flags, etc.
  }

  enum MessageType {
      Request,   // Client -> Server
      Response,  // Server -> Client
      Stream,    // Server -> Client (streaming chunk)
      Event,     // Server -> Client (status updates, notifications)
      Error,     // Either direction
  }

  2. Clean Protocol

  // Wire format: [4-byte length][JSON message]
  // No delimiters, no escaping needed
  [0x00, 0x00, 0x01, 0x2A] {"type": "request", "payload": {"command": "chat.switch", "args": [2]}}

  3. Simplified Server Architecture

  class MessageHandler:
      async def handle_message(self, message: Message) -> Optional[Message]:
          match message.type:
              case MessageType.Request:
                  return await self.handle_request(message)
              case MessageType.Response:
                  await self.handle_response(message)
              # etc.

  class CalousServer:
      async def process_connection(self, conn):
          async for message in self.read_messages(conn):
              response = await self.handler.handle_message(message)
              if response:
                  await self.send_message(conn, response)

  4. Status as Events

  # Status updates become events, not embedded in responses
  async def send_status_update(self):
      status_event = Message(
          type=MessageType.Event,
          payload={"event": "status_update", "data": self.get_status()}
      )
      await self.broadcast_event(status_event)

  5. Streaming Redesign

  # Model responses become proper streams
  async def handle_model_request(self, request):
      stream_id = generate_id()

      # Send initial response with stream info
      response = Message(
          type=MessageType.Response,
          id=request.id,
          payload={"stream_id": stream_id, "streaming": True}
      )
      await self.send_message(response)

      # Send chunks as separate stream messages
      async for chunk in model.stream_response():
          stream_msg = Message(
              type=MessageType.Stream,
              payload={"stream_id": stream_id, "chunk": chunk}
          )
          await self.send_message(stream_msg)

  6. Client Benefits

  // Client becomes much simpler
  impl CalousClient {
      async fn handle_message(&mut self, msg: Message) {
          match msg.type {
              MessageType::Response => self.handle_response(msg),
              MessageType::Stream => self.handle_stream_chunk(msg),
              MessageType::Event => self.handle_event(msg), // Status updates here
              MessageType::Error => self.handle_error(msg),
          }
      }
  }

  Key Benefits:

  1. No more delimiter hell - Length-prefixed messages
  2. Type safety - Structured JSON payloads
  3. Async-first - Natural streaming support
  4. Extensible - Easy to add new message types
  5. Debuggable - Clear message boundaries and types
  6. Testable - Mock messages easily

  Migration Strategy:

  1. Implement new protocol alongside old one
  2. Add version negotiation at connection start
  3. Gradually migrate client features
  4. Remove old protocol once stable

  The current protocol works, but this would eliminate most of the complexity and make future features much easier to implement. The
  risk is indeed high though - socket communication bugs are often subtle and hard to reproduce.

> how would you handle confirmation requests?

● Great question! Confirmation requests are one of the trickiest parts. Here's how I'd handle them in the cleaner protocol:

  Confirmation Flow Design

  1. Request-Response Pattern

  // Client sends command that might need confirmation
  {
    "type": "request",
    "id": "req_123",
    "payload": {
      "command": "history.clear",
      "args": []
    }
  }

  // Server responds with confirmation request
  {
    "type": "response",
    "id": "req_123",
    "payload": {
      "status": "needs_confirmation",
      "confirmation_id": "conf_456",
      "message": "Are you sure you want to clear chat history?",
      "default": "n",
      "options": ["y", "n"]
    }
  }

  // Client sends confirmation response
  {
    "type": "request",
    "id": "req_789",
    "payload": {
      "confirmation_id": "conf_456",
      "response": "y"
    }
  }

  // Server sends final result
  {
    "type": "response",
    "id": "req_789",
    "payload": {
      "status": "success",
      "message": "Chat history cleared"
    }
  }

  2. Server Implementation

  class ConfirmationManager:
      def __init__(self):
          self.pending_confirmations = {}

      async def request_confirmation(self, request_id: str, message: str, default: str = "n"):
          confirmation_id = f"conf_{uuid.uuid4().hex[:8]}"

          # Store the pending operation
          self.pending_confirmations[confirmation_id] = {
              "original_request_id": request_id,
              "pending_operation": lambda: self.execute_original_command(),
              "created_at": time.time()
          }

          return {
              "status": "needs_confirmation",
              "confirmation_id": confirmation_id,
              "message": message,
              "default": default,
              "options": ["y", "n"]
          }

      async def handle_confirmation_response(self, confirmation_id: str, response: str):
          if confirmation_id not in self.pending_confirmations:
              raise ValueError("Invalid confirmation ID")

          pending = self.pending_confirmations.pop(confirmation_id)

          if response.lower() in ["y", "yes"]:
              # Execute the original operation
              return await pending["pending_operation"]()
          else:
              return {"status": "cancelled", "message": "Operation cancelled"}

  3. Client Implementation

  impl CalousClient {
      async fn handle_confirmation_request(&mut self, response: Message) -> Result<()> {
          let payload = response.payload;
          let message = payload["message"].as_str().unwrap();
          let default = payload["default"].as_str().unwrap_or("n");
          let confirmation_id = payload["confirmation_id"].as_str().unwrap();

          // Show prompt to user
          let user_response = self.prompt_user(&format!("{} [{}]: ", message, default))?;
          let final_response = if user_response.trim().is_empty() {
              default.to_string()
          } else {
              user_response.trim().to_string()
          };

          // Send confirmation response
          let confirmation_msg = Message {
              type: MessageType::Request,
              id: Some(self.generate_id()),
              payload: json!({
                  "confirmation_id": confirmation_id,
                  "response": final_response
              }),
              metadata: HashMap::new()
          };

          self.send_message(confirmation_msg).await
      }
  }

  4. Alternative: Async/Await Style

  # Even cleaner - make confirmations feel synchronous
  async def clear_history(self, chat_id: int):
      # This would internally handle the confirmation flow
      confirmed = await self.confirm(
          "Are you sure you want to clear chat history?",
          default="n"
      )

      if confirmed:
          self.chat_history.clear(chat_id)
          return {"status": "success", "message": "History cleared"}
      else:
          return {"status": "cancelled", "message": "Operation cancelled"}

  class ConfirmationMixin:
      async def confirm(self, message: str, default: str = "n") -> bool:
          # Send confirmation request
          confirmation_id = await self.send_confirmation_request(message, default)

          # Wait for response (with timeout)
          response = await self.wait_for_confirmation(confirmation_id, timeout=30)

          return response.lower() in ["y", "yes"]

  5. Timeout Handling

  class ConfirmationManager:
      async def cleanup_expired_confirmations(self):
          """Background task to clean up expired confirmations"""
          while True:
              now = time.time()
              expired = [
                  conf_id for conf_id, data in self.pending_confirmations.items()
                  if now - data["created_at"] > 30  # 30 second timeout
              ]

              for conf_id in expired:
                  del self.pending_confirmations[conf_id]
                  # Optionally notify the client about timeout

              await asyncio.sleep(5)  # Check every 5 seconds

  Key Benefits:

  1. No threading needed - Async handles the waiting
  2. Timeout support - Confirmations don't hang forever
  3. Stateful but clean - Server tracks pending confirmations
  4. Testable - Easy to mock confirmation responses
  5. Type safe - Clear confirmation message structure
  6. Extensible - Could support multiple choice confirmations

  Error Handling:

  - Invalid confirmation IDs return errors
  - Timeouts automatically clean up state
  - Client disconnection cleans up pending confirmations
  - Duplicate confirmations are rejected

  This approach eliminates the current threading complexity while making confirmations feel natural to implement and use.
