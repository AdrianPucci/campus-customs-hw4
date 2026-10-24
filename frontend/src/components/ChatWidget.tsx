import { useEffect, useRef, useState, type FormEvent } from 'react'
import { sendChatMessage, type ChatMessage } from '../api/chat'

const GREETING: ChatMessage = {
  role: 'assistant',
  content: 'Hi! I’m the Campus Customs assistant. Ask me about Yale merch, prices, or sizes.',
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  // Keep the newest message in view.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    const userMessage: ChatMessage = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSending(true)
    try {
      const reply = await sendChatMessage(text, messages)
      setMessages((prev) => [...prev, reply])
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <section className="chat-panel" aria-label="Chat with Campus Customs">
          <header className="chat-header">
            <span>Campus Customs Chat</span>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>

          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.content}
              </div>
            ))}
            {sending && <div className="chat-bubble assistant muted">Typing…</div>}
            <div ref={endRef} />
          </div>

          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about merch…"
              aria-label="Your message"
            />
            <button type="submit" className="button" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : 'Chat'}
      </button>
    </div>
  )
}
