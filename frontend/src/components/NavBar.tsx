import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const LINKS = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

// Shown only to visitors who are not logged in.
const GUEST_LINKS = [
  { to: '/login', label: 'Log In' },
  { to: '/create-account', label: 'Create Account' },
]

export default function NavBar() {
  const { user, checking, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

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
          {!checking && !user &&
            GUEST_LINKS.map((link) => (
              <li key={link.to}>
                <NavLink to={link.to}>{link.label}</NavLink>
              </li>
            ))}
          {user && (
            <>
              <li className="nav-greeting">Hi, {user.first_name}</li>
              <li>
                <button type="button" className="nav-button" onClick={handleLogout}>
                  Log Out
                </button>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  )
}
