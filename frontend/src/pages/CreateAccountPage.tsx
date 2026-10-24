import { Link } from 'react-router-dom'

// Form only for now; creating the account is wired to the backend in a later problem.
export default function CreateAccountPage() {
  return (
    <section className="narrow">
      <h1>Create Account</h1>
      <form className="form" onSubmit={(e) => e.preventDefault()}>
        <label>
          First name
          <input name="first_name" autoComplete="given-name" required />
        </label>
        <label>
          Last name
          <input name="last_name" autoComplete="family-name" required />
        </label>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input type="password" name="password" autoComplete="new-password" minLength={8} required />
        </label>
        <button type="submit" className="button">
          Create Account
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
