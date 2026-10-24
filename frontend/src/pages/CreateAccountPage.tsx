import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const EMPTY = { first_name: '', last_name: '', email: '', password: '', confirm_password: '' }

export default function CreateAccountPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (field: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const mismatch = form.confirm_password !== '' && form.password !== form.confirm_password

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    // Checked here for a quick message; the backend checks the rest again.
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      // confirm_password stays in the browser; only the real fields are sent.
      const { confirm_password: _, ...data } = form
      await register(data)
      navigate('/products')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="narrow">
      <h1>Create Account</h1>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          First name
          <input name="first_name" autoComplete="given-name" required value={form.first_name} onChange={update('first_name')} />
        </label>
        <label>
          Last name
          <input name="last_name" autoComplete="family-name" required value={form.last_name} onChange={update('last_name')} />
        </label>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" required value={form.email} onChange={update('email')} />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={form.password}
            onChange={update('password')}
          />
          <span className="hint">At least 8 characters</span>
        </label>
        <label>
          Confirm password
          <input
            type="password"
            name="confirm_password"
            autoComplete="new-password"
            required
            value={form.confirm_password}
            onChange={update('confirm_password')}
            aria-invalid={mismatch}
          />
          {mismatch && <span className="error">Passwords do not match</span>}
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button type="submit" className="button" disabled={submitting || mismatch}>
          {submitting ? 'Creating account…' : 'Create Account'}
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
