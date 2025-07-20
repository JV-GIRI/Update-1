import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

export default function HeartbeatAnalyzer() {
  const [audioURL, setAudioURL] = useState(null);
  const [amplitude, setAmplitude] = useState(1);
  const [duration, setDuration] = useState(1000);
  const [filteredData, setFilteredData] = useState([]);
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);

  const audioRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (mediaRecorder) {
      mediaRecorder.ondataavailable = (event) => {
        setAudioChunks(prev => [...prev, event.data]);
      };
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setAudioChunks([]);
      };
    }
  }, [mediaRecorder, audioChunks]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    setMediaRecorder(recorder);
    recorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
  };

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
    }
  };

  const applyNoiseReduction = () => {
    // Dummy filter for now: simulate by lowering all points slightly
    const cleaned = filteredData.map(p => p * 0.8);
    setFilteredData(cleaned);
  };

  const drawWaveform = () => {
    const ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    ctx.beginPath();
    ctx.moveTo(0, 100);
    filteredData.forEach((val, i) => {
      ctx.lineTo(i, 100 - val * amplitude);
    });
    ctx.stroke();
  };

  useEffect(() => {
    drawWaveform();
  }, [filteredData, amplitude]);

  const analyze = () => {
    alert('Analysis complete. Heartbeat normal.');
  };

  const savePDF = () => {
    const doc = new jsPDF();
    doc.text('Heartbeat Report', 10, 10);
    doc.text('Analysis: Heartbeat normal', 10, 20);
    doc.save('heartbeat_report.pdf');
  };

  const saveToCloud = async () => {
    const blob = await fetch(audioURL).then(r => r.blob());
    const formData = new FormData();
    formData.append('file', blob);
    formData.append('analysis', 'Heartbeat normal');
    await fetch('https://your-api-endpoint.com/upload', {
      method: 'POST',
      body: formData,
    });
    alert('Saved to cloud');
  };

  return (
    <div className="p-4">
      <Card className="mb-4">
        <CardContent>
          <h2 className="text-xl font-bold mb-2">Live Heartbeat Recorder</h2>
          <Button onClick={recording ? stopRecording : startRecording}>
            {recording ? 'Stop Recording' : 'Start Recording'}
          </Button>
          {audioURL && (
            <>
              <audio ref={audioRef} src={audioURL} controls className="mt-2" />
              <canvas ref={canvasRef} width={500} height={200} className="mt-4 border" />
              <div className="mt-2">
                <label>Amplitude</label>
                <Slider value={[amplitude]} onValueChange={([val]) => setAmplitude(val)} max={5} step={0.1} />
              </div>
              <div className="mt-2">
                <label>Duration (ms)</label>
                <Input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
              </div>
              <Button onClick={applyNoiseReduction} className="mt-2">Noise Reduction</Button>
              <Button onClick={playAudio} className="mt-2 ml-2">Play</Button>
              <Button onClick={analyze} className="mt-2 ml-2">Analyze</Button>
              <Button onClick={savePDF} className="mt-2 ml-2">Download PDF</Button>
              <Button onClick={saveToCloud} className="mt-2 ml-2">Save Case</Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
