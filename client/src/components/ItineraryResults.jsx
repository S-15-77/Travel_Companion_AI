function ItineraryResults({data}){
    if (!data || data.length === 0) {
        return <p>No itinerary results found.</p>;
    return (
        <div className="result-box">
            <h3>Suggested Itinerary:</h3>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
    }
}
export default ItineraryResults;