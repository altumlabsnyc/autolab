import React, { useState } from 'react';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [output, setOutput] = useState('');

  const handleUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setLoading(true);
      setProgress(0);

      // Simulating the upload process
      const uploadInterval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress + 1;
          if (newProgress >= 10) {
            clearInterval(uploadInterval);
            setLoading(false);
            setOutput("Lab script generated.\n Procedure:\n Step 1: ...\n Step 2: ...");
          }
          return newProgress;
        });
      }, 500);
    }
  };

  return (
    <div className="container">
      <h1>Welcome to AutoLab by @AltumLabs</h1>
      <h3>AutoLab is a proprietary API developed by Altum Labs. Its purpose is to convert wet lab procedures into a procedural list for use in lab reports in an effortless and accurate way by utilizing AI algorithms. All data will be deleted from the server immediately after processing it.</h3>
      <h4>Instructions of use</h4>
      <body>Upload a .mp4 or .mp3 recording of a wet lab procedure. Autolab will automatically analyze the audio and process it into a professional grade procedure that can serve as a foundation to the procedural section of the lab report. Please note that this process takes time. You will be able to see a progress bar.</body>
      <h4>Disclaimer</h4>
      <body>
      Our transcription service is automated and may not be 100% accurate. Factors like recording quality, background noise, accents, and technical limitations can impact accuracy. We recommend reviewing and editing transcriptions for accuracy and clarity. Use the service at your own risk, acknowledging that it's provided 'as-is' and subject to our terms and conditions.
      </body>
      <h2>Step 1. Upload file here</h2>
      <input type="file" accept=".mp4,.mp3" onChange={handleUpload} />
      
      {loading && <div>Uploading... {progress*10}%</div>}
      {output && <div>{output}</div>}
    </div>
  );
};

export default App;
