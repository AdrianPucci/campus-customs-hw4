import { createContext, useContext, useState, type ReactNode } from 'react'
import type { ProductCard } from '../types'

export interface ChatResults {
  question: string // what the shopper asked, shown as the section title
  products: ProductCard[]
}

interface ChatResultsState {
  results: ChatResults | null
  showResults: (results: ChatResults) => void
  clearResults: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

// Shares the agent's latest matching products between the chat panel (which sets them)
// and the on-page "Matching items" section (which shows them).
export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(null)
  return (
    <ChatResultsContext.Provider
      value={{ results, showResults: setResults, clearResults: () => setResults(null) }}
    >
      {children}
    </ChatResultsContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used inside <ChatResultsProvider>')
  return ctx
}
