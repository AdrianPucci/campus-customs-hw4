import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useChatResults } from '../chat/ChatResultsContext'

// The products the chat agent found, shown as cards at the top of whatever page is open.
export default function MatchingProducts() {
  const { results, clearResults } = useChatResults()
  const sectionRef = useRef<HTMLElement>(null)

  // Bring the new cards into view each time the agent finds something.
  useEffect(() => {
    if (results) sectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [results])

  if (!results) return null

  return (
    <section ref={sectionRef} className="matching" aria-label="Matching items from chat">
      <header className="matching-header">
        <div>
          <p className="eyebrow">From your chat</p>
          <h2>
            {results.products.length} matching item{results.products.length === 1 ? '' : 's'}
            <span className="matching-question"> for “{results.question}”</span>
          </h2>
        </div>
        <button type="button" className="matching-close" onClick={clearResults} aria-label="Hide matching items">
          ×
        </button>
      </header>

      <div className="product-grid">
        {results.products.map((p) => (
          <Link key={p.product_id} to={`/products/${p.product_id}`} className="product-card match-card">
            <img src={p.image_url} alt={p.name} loading="lazy" />
            <h3>{p.name}</h3>
            <p className="price">${p.price.toFixed(2)}</p>
            <p className="match-info">{p.short_info}</p>
            <p className={p.in_stock ? 'match-sizes' : 'match-sizes sold-out'}>
              {p.in_stock ? `In stock: ${p.sizes_in_stock.join(' · ')}` : 'Sold out'}
            </p>
          </Link>
        ))}
      </div>
    </section>
  )
}
