import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { loadChatHistory, sendChatMessage, type ChatMessage } from '../api/chat'
import { useAuth } from '../auth/AuthContext'
import { useChatResults } from '../chat/ChatResultsContext'
import { chatSuggestions } from '../chat/suggestions'

// More matches than this are shown only on the page, not squeezed into the chat panel.
const MAX_CARDS_IN_PANEL = 4

const GREETING: ChatMessage = {
  role: 'assistant',
  content: 'Hi! I’m the Campus Customs assistant. Ask me about Yale merch, prices, or sizes.',
}

// Shows **bold** from the agent's replies as bold text. Built from React elements,
// not HTML, so nothing in a reply can inject code into the page.
function withBold(text: string) {
  return text.split('**').map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part))
}

// App.tsx gives this component key={user id}, so logging in or out starts a fresh panel.
export default function ChatWidget() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    user ? { role: 'assistant', content: `Welcome back, ${user.first_name}! Your chats are saved to your account.` } : GREETING,
  ])

  // Logged in: reload the saved conversation under the greeting.
  useEffect(() => {
    if (!user) return
    loadChatHistory().then((saved) => setMessages((prev) => [prev[0], ...saved]))
  }, [user])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [status, setStatus] = useState('') // the agent's current step, streamed from the backend
  const [askedThisVisit, setAskedThisVisit] = useState(false) // hides the suggestion chips once used
  const endRef = useRef<HTMLDivElement>(null)
  const { showResults } = useChatResults()
  const { pathname } = useLocation()

  // Keep the newest message in view.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    send(input)
  }

  async function send(raw: string) {
    const text = raw.trim()
    if (!text || sending) return

    const userMessage: ChatMessage = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSending(true)
    setAskedThisVisit(true)
    setStatus('💭 Thinking about your question…')
    try {
      // The greeting is just for the screen; the agent only needs the real conversation.
      const viewing = pathname.startsWith('/products/') ? decodeURIComponent(pathname.slice('/products/'.length)) : null
      // Swap the shopper's bubble for the cleaned text as soon as the backend reports a redaction.
      const showRedacted = (shownMessage: string, notice: string) =>
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'user', content: shownMessage },
          { role: 'assistant', content: '', notice },
        ])
      const reply = await sendChatMessage(text, messages.slice(1), viewing, setStatus, showRedacted)
      // The notice was already shown when the redaction arrived, so the reply doesn't repeat it.
      setMessages((prev) => [...prev, { ...reply, notice: reply.shownMessage ? undefined : reply.notice }])
      // Matching items also appear as full cards on the page itself.
      if (reply.products?.length)
        showResults({ question: reply.shownMessage ?? text, products: reply.products, askedOn: pathname })
    } catch (err) {
      // Rate-limit and server messages are already written for shoppers, so show them as-is.
      setMessages((prev) => [...prev, { role: 'assistant', content: (err as Error).message }])
    } finally {
      setSending(false)
      setStatus('')
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
                {m.notice && <p className="chat-notice">{m.notice}</p>}
                {m.content && <div className={`chat-bubble ${m.role}`}>{withBold(m.content)}</div>}
                {/* Matching items from the agent, each linking to its product page */}
                {m.products && m.products.length > MAX_CARDS_IN_PANEL && (
                  <p className="chat-note">See all {m.products.length} items on the page ↖</p>
                )}
                {m.products && m.products.length > 0 && m.products.length <= MAX_CARDS_IN_PANEL && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat-product">
                        <img src={p.image_url} alt="" />
                        <span className="chat-product-name">{p.name}</span>
                        <span className="price">${p.price.toFixed(2)}</span>
                        <span className="chat-product-sizes">
                          {p.in_stock ? p.sizes_in_stock.join(' · ') : 'Sold out'}
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {!askedThisVisit && !sending && (
              <div className="chat-suggestions" aria-label="Suggested questions">
                {chatSuggestions().map((s) => (
                  <button key={s.label} type="button" className="chat-chip" onClick={() => send(s.question)}>
                    {s.label}
                  </button>
                ))}
              </div>
            )}
            {sending && (
              <div className="chat-bubble assistant chat-status" role="status" aria-live="polite">
                <span className="chat-status-step">{status}</span>
                <span className="chat-status-soon">Hang tight, your results are almost here! 🐾</span>
              </div>
            )}
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
          <p className="chat-disclosure">AI assistant · can make mistakes · never share payment info</p>
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
