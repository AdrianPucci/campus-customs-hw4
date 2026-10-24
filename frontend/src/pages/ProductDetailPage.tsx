import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { Product } from '../types'

export default function ProductDetailPage() {
  // The product_id comes from the URL, e.g. /products/yale-mom-hoodie
  const { productId } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`/api/products/${encodeURIComponent(productId ?? '')}`)
      .then((res) => {
        if (res.status === 404) throw new Error('That product does not exist.')
        if (!res.ok) throw new Error('Could not load this product. Is the backend running?')
        return res.json()
      })
      .then((data: Product) => setProduct(data))
      .catch((err: Error) => setError(err.message))
  }, [productId])

  if (error) {
    return (
      <section className="narrow">
        <p className="error">{error}</p>
        <Link to="/products">← Back to Products</Link>
      </section>
    )
  }
  if (!product) return <p className="muted">Loading…</p>

  return (
    <section>
      <Link to="/products" className="back-link">
        ← Back to Products
      </Link>
      <div className="product-detail">
        <img src={product.image_url} alt={product.name} className="detail-image" />

        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price detail-price">${product.price.toFixed(2)}</p>
          <p>{product.description}</p>

          <h2>Colors</h2>
          <p>{product.colors.join(', ')}</p>

          <h2>Sizes &amp; stock</h2>
          <ul className="size-list">
            {product.inventory.map((s) => (
              <li key={s.size} className={s.quantity === 0 ? 'sold-out' : ''}>
                <strong>{s.size}</strong>
                <span>{s.quantity === 0 ? 'Sold out' : `${s.quantity} in stock`}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
