import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Product } from '../types'

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Load the catalogue once, when the page opens.
  useEffect(() => {
    fetch('/api/products')
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json()
      })
      .then((data: Product[]) => setProducts(data))
      .catch(() => setError('Could not load products. Is the backend running on port 8000?'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section>
      <h1>Products</h1>
      {loading && <p className="muted">Loading products…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && <p className="muted">{products.length} items</p>}

      <div className="product-grid">
        {products.map((p) => (
          <Link key={p.product_id} to={`/products/${p.product_id}`} className="product-card">
            <img src={p.image_url} alt={p.name} loading="lazy" />
            <h2>{p.name}</h2>
            <p className="price">${p.price.toFixed(2)}</p>
          </Link>
        ))}
      </div>
    </section>
  )
}
