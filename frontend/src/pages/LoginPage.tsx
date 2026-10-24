import { Link } from 'react-router-dom'

// Form only for now; signing in is wired to the backend in a later problem.
export default function LoginPage() {
  return (
    <section className="narrow">
      <h1>Log In</h1>
      <form className="form" onSubmit={(e) => e.preventDefault()}>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input type="password" name="password" autoComplete="current-password" required />
        </label>
        <button type="submit" className="button">
          Log In
        </button>
      </form>
      <p className="muted">
        New here? <Link to="/create-account">Create an account</Link>
      </p>
    </section>
  )
}
