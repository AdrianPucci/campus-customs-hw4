import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <section className="hero">
      <h1>Yale Bulldog Blue</h1>
      <p>Officially licensed Yale apparel from Campus Customs: hoodies, crewnecks, tees and more.</p>
      <Link to="/products" className="button">
        Shop Products
      </Link>
    </section>
  )
}
