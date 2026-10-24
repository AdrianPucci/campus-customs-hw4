import SeasonalTag from './SeasonalTag'

// A short graffiti band under the Home video, with the seasonal tag on it. The wall is original
// artwork drawn in code (scripts/make_graffiti.py → public/graffiti-wall.svg), so it's ours to use,
// inspired by New Haven street art in coral, teal, olive and navy.
const GRAFFITI_WALL = '/graffiti-wall.svg'

export default function GraffitiStrip() {
  return (
    <section className="graffiti-strip" style={{ backgroundImage: `url(${GRAFFITI_WALL})` }} aria-label="New Haven street art">
      <SeasonalTag />
      <span className="graffiti-credit">New Haven, CT</span>
    </section>
  )
}
