import type { ProductCard } from '../types'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: ProductCard[] // items the assistant matched, shown under its reply
}

// A logged-in shopper's saved conversation (oldest first). Guests get an empty list.
export async function loadChatHistory(): Promise<ChatMessage[]> {
  const res = await fetch('/api/chat/history')
  if (!res.ok) return []
  const data = await res.json()
  return data.messages as ChatMessage[]
}

// Sends the message plus earlier turns to the backend's PydanticAI agent.
// The session cookie goes along automatically, so the agent knows who is logged in.
export async function sendChatMessage(message: string, history: ChatMessage[]): Promise<ChatMessage> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history: history.map(({ role, content }) => ({ role, content })), // text only, no product data
    }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The assistant is unavailable right now.')
  return { role: 'assistant', content: data.reply, products: data.products }
}
