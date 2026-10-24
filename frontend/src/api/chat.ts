import type { ProductCard } from '../types'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: ProductCard[] // items the assistant matched, shown under its reply
  notice?: string // safety notice, e.g. a card number was removed from the shopper's message
  shownMessage?: string // the shopper's message after redaction, shown in place of what they typed
}

// A logged-in shopper's saved conversation (oldest first). Guests get an empty list.
export async function loadChatHistory(): Promise<ChatMessage[]> {
  const res = await fetch('/api/chat/history')
  if (!res.ok) return []
  const data = await res.json()
  return data.messages as ChatMessage[]
}

// Sends the message plus earlier turns to the backend's PydanticAI agent and calls
// onStatus with each step the agent takes ("📦 Checking stock by size…") as it happens.
// The backend answers with one JSON object per line: status lines, then a "done" line.
// The session cookie goes along automatically, so the agent knows who is logged in.
export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  viewingProductId: string | null = null, // product page that's open, so "this" makes sense
  onStatus: (text: string) => void = () => {},
  onRedacted: (shownMessage: string, notice: string) => void = () => {}, // sensitive data was removed
): Promise<ChatMessage> {
  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      // text only, no product data; notice-only entries (no text) aren't part of the conversation
      history: history.filter((m) => m.content).map(({ role, content }) => ({ role, content })),
      viewing_product_id: viewingProductId,
    }),
  })
  if (!res.ok || !res.body) {
    const data = await res.json().catch(() => ({}))
    throw new Error(typeof data.detail === 'string' ? data.detail : 'The assistant is unavailable right now.')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    buffer += decoder.decode(value, { stream: !done })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? '' // keep a partial last line until the rest arrives
    for (const line of lines) {
      if (!line.trim()) continue
      const event = JSON.parse(line)
      if (event.type === 'status') onStatus(event.text)
      else if (event.type === 'redacted') onRedacted(event.shown_message, event.notice)
      else if (event.type === 'done')
        return {
          role: 'assistant',
          content: event.reply,
          products: event.products,
          notice: event.notice ?? undefined,
          shownMessage: event.shown_message ?? undefined,
        }
      else if (event.type === 'error') throw new Error(event.detail)
    }
    if (done) break
  }
  throw new Error('The assistant stopped before answering. Please try again.')
}
