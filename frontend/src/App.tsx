import { Route, Routes } from 'react-router-dom'
import ChatWidget from './components/ChatWidget'
import MatchingProducts from './components/MatchingProducts'
import NavBar from './components/NavBar'
import AboutPage from './pages/AboutPage'
import CreateAccountPage from './pages/CreateAccountPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import ProductDetailPage from './pages/ProductDetailPage'
import ProductsPage from './pages/ProductsPage'

export default function App() {
  return (
    <>
      <NavBar />
      <main className="page">
        <MatchingProducts />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer className="site-footer">
        © 2026 Yale Bulldog Blue by Campus Customs · Class project, not the real store
      </footer>
      <ChatWidget />
    </>
  )
}
