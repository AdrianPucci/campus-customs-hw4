import SeasonalTag from './SeasonalTag'

// A short band of New Haven street graffiti under the Home video, with the seasonal tag on it.
// The photo lives in data/hero/ (not in git), served at /media/hero/; without it the band
// shows a Yale-blue and fall-orange street-stripe pattern instead.
const GRAFFITI_PHOTO = '/media/hero/new-haven-graffiti.jpg'

export default function GraffitiStrip() {
  return (
    <section className="graffiti-strip" style={{ backgroundImage: `url(${GRAFFITI_PHOTO})` }} aria-label="New Haven street art">
      <SeasonalTag />
      <span className="graffiti-credit">New Haven, CT</span>
    </section>
  )
}
