// Tappable starter questions for the chat. Two of them change with the calendar:
// a seasonal pick and the Yale sport that's in season. Month is 0-11 (January = 0).

export interface Suggestion {
  label: string // what the chip shows
  question: string // what gets sent to the agent when tapped
}

const GIFTS: Suggestion = {
  label: '🎁 Gift ideas',
  question: 'What are some good Yale gift ideas for family, like a mom, dad or grandparent?',
}

function seasonal(month: number): Suggestion {
  if (month === 10) {
    // November: The Game (Harvard-Yale) and the start of gift season
    return { label: '🏟️ The Game gear', question: 'What do you have for Harvard-Yale weekend?' }
  }
  if (month === 11 || month <= 1) {
    return { label: '❄️ Cozy winter picks', question: 'What are your warmest jackets, fleeces and hoodies for winter?' }
  }
  if (month <= 4) {
    return { label: '🌸 Spring layers', question: 'What light layers like crewnecks and quarter-zips do you have for spring?' }
  }
  if (month <= 7) {
    return { label: '☀️ Summer tees', question: 'What T-shirts do you have for summer?' }
  }
  return { label: '🍂 Fall layers', question: 'What hoodies and quarter-zips do you have for fall?' }
}

// Yale sports in season, roughly: fall football/soccer, winter hockey/basketball,
// spring baseball/lacrosse, summer baseball/sailing. The first one gets the chip.
const SPORTS_BY_SEASON: { months: number[]; emoji: string; sport: string }[] = [
  { months: [8, 9, 10], emoji: '🏈', sport: 'football' },
  { months: [11, 0, 1], emoji: '🏒', sport: 'hockey' },
  { months: [2, 3, 4], emoji: '⚾', sport: 'baseball' },
  { months: [5, 6, 7], emoji: '⚾', sport: 'baseball' },
]

function sportInSeason(month: number): Suggestion {
  const s = SPORTS_BY_SEASON.find((x) => x.months.includes(month)) ?? SPORTS_BY_SEASON[0]
  return {
    label: `${s.emoji} ${s.sport[0].toUpperCase()}${s.sport.slice(1)} season`,
    question: `It's ${s.sport} season! What ${s.sport} gear do you have?`,
  }
}

export function chatSuggestions(today: Date = new Date()): Suggestion[] {
  const month = today.getMonth()
  return [GIFTS, seasonal(month), sportInSeason(month)]
}
