import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { sendChatMessage, type ChatMessage } from '../api/chat'

const GREETING: ChatMessage = {
  role: 'assistant',
  content: 'Hi! I’m the Campus Customs assistant. Ask me about Yale merch, prices, or sizes.',
}

// Shows **bold** from the agent's replies as bold text. Built from React elements,
// not HTML, so nothing in a reply can inject code into the page.
function withBold(text: string) {
  return text.split('**').map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part))
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
      // The greeting is just for the screen; the agent only needs the real conversation.
      const reply = await sendChatMessage(text, messages.slice(1))
      setMessages((prev) => [...prev, reply])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Sorry, ${(err as Error).message}` }])
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
              <div key={i} className={`chat-turn ${m.role}`}>
                <div className={`chat-bubble ${m.role}`}>{withBold(m.content)}</div>
                {/* Matching items from the agent, each linking to its product page */}
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat-product">
                        <img src={p.image_url} alt="" />
                        <span className="chat-product-name">{p.name}</span>
                        <span className="price">${p.price.toFixed(2)}</span>
                      </Link>
                    ))}
                  </div>
                )}
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
