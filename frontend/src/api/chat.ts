export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// STUB: answers locally for now. In a later problem this becomes
//   fetch('/api/chat', { method: 'POST', body: JSON.stringify({ message, history }) })
// so the PydanticAI agent on the backend writes the reply. The chat panel only
// calls this function, so nothing else has to change when that happens.
export async function sendChatMessage(message: string, history: ChatMessage[]): Promise<ChatMessage> {
  void history // will be sent to the backend later
  await new Promise((resolve) => setTimeout(resolve, 400)) // feels like a real request
  return {
    role: 'assistant',
    content: `Thanks for asking about "${message}". I'm not connected to the shop yet. Soon I'll be able to find merch and check sizes and stock for you.`,
  }
}
