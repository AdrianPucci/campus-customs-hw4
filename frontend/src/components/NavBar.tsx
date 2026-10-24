import { Link, NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
  { to: '/login', label: 'Log In' },
  { to: '/create-account', label: 'Create Account' },
]

export default function NavBar() {
  return (
    <header className="site-header">
      <div className="announcement">Officially Licensed Merchandise</div>
      <nav className="navbar">
        <Link to="/" className="logo" aria-label="Yale Bulldog Blue home">
          <span className="logo-yale">YALE</span>
          <span className="logo-sub">BULLDOG BLUE</span>
        </Link>
        <ul className="nav-links">
          {LINKS.map((link) => (
            <li key={link.to}>
              {/* NavLink adds the "active" class when its page is open */}
              <NavLink to={link.to} end={link.to === '/'}>
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  )
}
