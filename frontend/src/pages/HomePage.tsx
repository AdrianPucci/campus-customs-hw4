import { Link } from 'react-router-dom'
import GraffitiStrip from '../components/GraffitiStrip'

// Muted, looping clip from the Campus Customs ad behind the heading. The poster (the wide
// crew shot) shows while it loads, and instead of the video for people who prefer less motion.
// Both files live in data/hero/ (not in git); without them the banner falls back to Yale blue.
const HERO_VIDEO = '/media/hero/hero-loop.mp4'
const HERO_POSTER = '/media/hero/hero-poster.jpg'

export default function HomePage() {
  return (
    <>
    <section className="hero-banner">
      <video className="hero-media" src={HERO_VIDEO} poster={HERO_POSTER} autoPlay muted loop playsInline aria-hidden="true" />
      <div className="hero-overlay" />
      <div className="hero-stripes" aria-hidden="true" />
      <div className="hero-content">
        <p className="hero-eyebrow">Officially licensed · Campus Customs</p>
        <h1>Wear the Blue.</h1>
        <p>Hoodies, crewnecks, tees and more for Bulldogs everywhere: students, families and alumni.</p>
        <div className="hero-actions">
          <Link to="/products" className="button hero-button">
            Shop Products
          </Link>
          <span className="hero-hint">or ask our chat for ideas ↘</span>
        </div>
      </div>
    </section>
    <GraffitiStrip />
    </>
  )
}
