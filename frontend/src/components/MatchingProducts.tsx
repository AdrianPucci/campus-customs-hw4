import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useChatResults } from '../chat/ChatResultsContext'

// The products the chat agent found, shown as cards at the top of whatever page is open.
// On a single-product page it shrinks to one line, so the detail view stays in sight.
export default function MatchingProducts() {
  const { results, clearResults } = useChatResults()
  const { pathname } = useLocation()
  const sectionRef = useRef<HTMLElement>(null)
  const onDetailPage = pathname.startsWith('/products/')
  // Remembers which page + results the shopper expanded; any new page or new results collapse it again.
  const [expandedAt, setExpandedAt] = useState<{ pathname: string; results: unknown } | null>(null)
  const expanded = expandedAt?.pathname === pathname && expandedAt.results === results
  const setExpanded = () => setExpandedAt({ pathname, results })

  // New results: bring them into view.
  useEffect(() => {
    if (results) sectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [results])

  if (!results) return null
  const count = results.products.length
  const label = `${count} matching item${count === 1 ? '' : 's'}`

  // Collapse only after the shopper has clicked through to a product, not where they asked.
  if (onDetailPage && pathname !== results.askedOn && !expanded) {
    return (
      <section ref={sectionRef} className="matching-bar" aria-label="Matching items from chat">
        <button type="button" className="link-button" onClick={setExpanded}>
          ← Back to your {label} from chat
        </button>
        <button type="button" className="matching-close" onClick={clearResults} aria-label="Hide matching items">
          ×
        </button>
      </section>
    )
  }

  return (
    <section ref={sectionRef} className="matching" aria-label="Matching items from chat">
      <header className="matching-header">
        <div>
          <p className="eyebrow">From your chat</p>
          <h2>
            {label}
            <span className="matching-question"> for “{results.question}”</span>
          </h2>
        </div>
        <button type="button" className="matching-close" onClick={clearResults} aria-label="Hide matching items">
          ×
        </button>
      </header>

      <div className="product-grid">
        {results.products.map((p) => (
          // Same detail route as the Products page cards: /products/<product_id>
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
