import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AnomalyStats(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [anomalies, setAnomalies] = useState({});
    const [error, setError] = useState(null)

	const getAnomaly = () => {
	
        fetch(`http://ec2-44-230-66-254.us-west-2.compute.amazonaws.com/anomaly/${props.eventType}`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Anomaly Results for " + props.eventType)
                setAnomalies(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getAnomaly(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getAnomaly]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
             <div style={{ fontFamily: 'Arial, sans-serif' }}>
            {anomalies && anomalies.length > 0 ? (
                <div>
                    <div>
                        {props.eventType} Latest Anomaly 
                        UUID:{anomalies[0].event_id}
                        {anomalies[0].description}
                        Detected on {anomalies[0].timestamp}
                    </div>
                </div>
            ) : (
                <div>No {props.eventType} anomalies found</div>
            )}
        </div>
        )
    }
}
