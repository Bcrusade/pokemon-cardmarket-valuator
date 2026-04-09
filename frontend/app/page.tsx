export default function HomePage() {
  return (
    <main style={{ maxWidth: 700, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Pokemon Cardmarket Valuator</h1>
      <p>Minimal MVP scaffold.</p>
      <ul>
        <li>Backend API with job workflow endpoints</li>
        <li>Deterministic pricing engine</li>
        <li>Cards-to-clarify routing for uncertain matches</li>
      </ul>
      <p>
        Start backend at <code>http://localhost:8000</code> and frontend at <code>http://localhost:3000</code>.
      </p>
    </main>
  );
}
