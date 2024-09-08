import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the backend every 15 seconds
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('http://localhost:5000/events');
        console.log(response.data);
        setEvents(response.data);
      } catch (error) {
        setError(error.message);
        console.error("Error fetching events:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData(); // Fetch immediately on mount
    const interval = setInterval(fetchData, 15000); // Fetch every 15 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <div className="App">
      <h1>GitHub Events</h1>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <ul>
        {events.map((event, index) => (
          <li key={index}>
            {event.event_type === 'push' && (
              <p>
                {event.author} pushed to {event.to_branch} on {new Date(event.timestamp).toLocaleString()}
              </p>
            )}
            {event.event_type === 'pull_request' && (
              <p>
                {event.author} submitted a pull request from {event.from_branch} to {event.to_branch} on {new Date(event.timestamp).toLocaleString()}
              </p>
            )}
            {event.event_type === 'merge' && (
              <p>
                {event.author} merged branch {event.from_branch} to {event.to_branch} on {new Date(event.timestamp).toLocaleString()}
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
