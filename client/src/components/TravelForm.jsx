import { useState } from 'react';
import axios from 'axios';

function TravelForm() {
  const [destination, setDestination] = useState('');
  const [days, setDays] = useState('');
  const [interests, setInterests] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);
    try {
      const res = await axios.post('http://localhost:8000/plan-trip', {
        destination,
        days: parseInt(days),
        interests,
      });
      setResponse(res.data);
    } catch (error) {
      console.error("Error generating itinerary:", error);
      setResponse({
        destination,
        days,
        interests: [interests],
        message: "Sorry, there was an error generating your itinerary. Please try again."
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSurpriseMe = () => {
    setInterests('beaches, museums, nightlife');
  };

  return (
    <section id="planner" className="form-section fade-in">
      <div className="glass-card">
        <h2 className="fade-in">Plan Your Trip</h2>

        <form onSubmit={handleSubmit} className="trip-form">
          <input
            type="text"
            placeholder="Destination (e.g., Italy)"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          />

          <input
            type="number"
            placeholder="Number of Days (e.g., 5)"
            value={days}
            onChange={(e) => setDays(e.target.value)}
            required
          />

          <input
            type="text"
            placeholder="Interests (e.g., beaches, food, history)"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
          />

          <button
            type="button"
            className="surprise-btn"
            onClick={handleSurpriseMe}
          >
            🎲 Surprise Me
          </button>

          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Itinerary'}
          </button>
        </form>

        {loading && (
          <div className="itinerary-card fade-in">
            <p>🤖 AI is crafting your perfect itinerary...</p>
          </div>
        )}

        {response && !loading && (
          <div className="itinerary-card fade-in">
            <h3>🧳 Your AI-Powered Itinerary</h3>
            <p><strong>Destination:</strong> {response.destination}</p>
            <p><strong>Duration:</strong> {response.days} days</p>
            <p><strong>Interests:</strong> {Array.isArray(response.interests) ? response.interests.join(', ') : response.interests}</p>
            <p style={{ marginTop: '1rem' }}>{response.message}</p>
          </div>
        )}
      </div>
    </section>
  );
}

export default TravelForm;