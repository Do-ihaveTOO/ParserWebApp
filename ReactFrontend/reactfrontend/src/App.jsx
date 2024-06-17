import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { v4 as uuidv4 } from 'uuid';

const baseURL = 'http://192.168.50.51:5000';

function App() {
    const [output, setOutput] = useState({});
    const [loading, setLoading] = useState(false);
    const [sessionId] = useState(uuidv4());

    const startScript = async (name) => {
        try {
            setLoading(true);
            await axios.post(`${baseURL}/start`, { name, session_id: sessionId });
            fetchOutput();
        } catch (error) {
            console.error('Error starting script:', error);
        } finally {
            setLoading(false);
        }
    };

    const stopScripts = async () => {
        try {
            setLoading(true);
            await axios.post(`${baseURL}/stop`, { session_id: sessionId });
            fetchOutput();
        } catch (error) {
            console.error('Error stopping scripts:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchOutput = async () => {
        try {
            const response = await axios.get(`${baseURL}/output`, { params: { session_id: sessionId } });
            setOutput(response.data);
        } catch (error) {
            console.error('Error fetching output:', error);
        }
    };

    const exportOutput = async () => {
        try {
            const response = await axios.get(`${baseURL}/export`, { params: { session_id: sessionId }, responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'output.txt');
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Error exporting output:', error);
        }
    };

    useEffect(() => {
        fetchOutput();
        const interval = setInterval(fetchOutput, 5000);
        return () => clearInterval(interval);
    }, [sessionId]);

    return (
        <div className="App">
            <h1>Script Runner</h1>
            <div className="button-group">
                <button onClick={() => startScript('DESP')} disabled={loading}>Start Despatch</button>
                <button onClick={() => startScript('OA')} disabled={loading}>Start OA</button>
                <button onClick={() => startScript('PO')} disabled={loading}>Start PO</button>
                <button onClick={() => startScript('BS')} disabled={loading}>Start BS</button>
                <button onClick={() => startScript('AM')} disabled={loading}>Start AM</button>
            </div>
            <button onClick={stopScripts} disabled={loading}>Stop All Scripts</button>
            <button onClick={exportOutput} disabled={loading}>Export Output</button>
            <div className="output">
                {Object.entries(output).map(([name, text]) => (
                    <div key={name}>
                        <h3>{name}</h3>
                        <pre>{text}</pre>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
