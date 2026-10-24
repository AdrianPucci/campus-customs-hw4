import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// React Router keeps the scroll position between pages; start each new page at the top
// so a product's large image and details are the first thing the shopper sees.
export default function ScrollToTop() {
  const { pathname } = useLocation()
  // Braces matter: newer browsers return a Promise from scrollTo, and an effect
  // may only return a clean-up function, so returning it crashes React.
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}
