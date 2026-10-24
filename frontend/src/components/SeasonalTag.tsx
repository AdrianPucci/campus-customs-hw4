// A small spray-paint style tag with a few drifting seasonal shapes (fall leaves now).
// Kept deliberately light: one short word, three shapes, slow motion, hidden for reduced motion.

const SEASONS = [
  { months: [8, 9, 10], word: 'Boola Boola', shape: 'leaf', colors: ['#c8742b', '#a8432a', '#d9a441'] },
  { months: [11, 0, 1], word: 'Bulldogs', shape: 'flake', colors: ['#ffffff', '#cfe0f2', '#ffffff'] },
  { months: [2, 3, 4], word: 'Bulldogs', shape: 'petal', colors: ['#f2b8c6', '#ffffff', '#f2b8c6'] },
  { months: [5, 6, 7], word: 'Boola Boola', shape: 'leaf', colors: ['#5d8a3a', '#7aa84f', '#5d8a3a'] },
]

const SHAPES: Record<string, string> = {
  // simple maple-ish leaf, snowflake and petal outlines (24x24 viewBox)
  leaf: 'M12 2l2 4 4-1-1 4 4 2-4 2 1 4-4-1-2 6-2-6-4 1 1-4-4-2 4-2-1-4 4 1z',
  flake: 'M11 2h2v7l5-4 1 2-5 4h7v2h-7l5 4-1 2-5-4v7h-2v-7l-5 4-1-2 5-4H2v-2h7L4 7l1-2 5 4z',
  petal: 'M12 3c4 3 5 8 0 15C7 11 8 6 12 3z',
}

const THIS_MONTH = new Date().getMonth() // read once when the page loads

export default function SeasonalTag({ month = THIS_MONTH }: { month?: number }) {
  const season = SEASONS.find((s) => s.months.includes(month)) ?? SEASONS[0]
  return (
    <div className="seasonal-tag" aria-hidden="true">
      <span className="graffiti">{season.word}</span>
      {season.colors.map((color, i) => (
        <svg key={i} className={`drift drift-${i}`} viewBox="0 0 24 24" width="18" height="18">
          <path d={SHAPES[season.shape]} fill={color} />
        </svg>
      ))}
    </div>
  )
}
