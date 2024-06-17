const video = document.getElementById("video");
const recognitionThreshold = 5;
let recognitionCount = 0;

Promise.all([
  faceapi.nets.ssdMobilenetv1.loadFromUri("/models"),
  faceapi.nets.faceRecognitionNet.loadFromUri("/models"),
  faceapi.nets.faceLandmark68Net.loadFromUri("/models"),
]).then(startWebcam);

function startWebcam() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(error => {
      console.error('Error accessing the webcam', error);
    });
}

async function getLabeledFaceDescriptions() {
    const response = await fetch('/get-user-ids');
    const labels = await response.json();

    return Promise.all(
        labels.map(async label => {
            const descriptions = [];
            for (let i = 1; i <= 5; i++) {
                const img = await faceapi.fetchImage(`/snapshots/${label}/${i}.jpeg`);
                const detections = await faceapi.detectSingleFace(img).withFaceLandmarks().withFaceDescriptor();
                if (detections) {
                    descriptions.push(detections.descriptor);
                }
            }
            return new faceapi.LabeledFaceDescriptors(label.toString(), descriptions);
        })
    );
}

video.addEventListener('play', async () => {
  const labeledFaceDescriptors = await getLabeledFaceDescriptions();
  const faceMatcher = new faceapi.FaceMatcher(labeledFaceDescriptors, 0.6);
  const canvas = faceapi.createCanvasFromMedia(video);
  const videoContainer = document.querySelector('.video-container');
  videoContainer.append(canvas);
  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);

  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(video).withFaceLandmarks().withFaceDescriptors();
    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

    const results = resizedDetections.map(d => faceMatcher.findBestMatch(d.descriptor));
    results.forEach((result, i) => {
      const box = resizedDetections[i].detection.box;
      const drawBox = new faceapi.draw.DrawBox(box, { label: result.toString() });
      drawBox.draw(canvas);

      if (result.label !== 'unknown') {
        recognitionCount++;
        if (recognitionCount >= recognitionThreshold) {
          document.querySelector('input[name="user_id"]').value = result.label;
          recognitionCount = 0; 
          console.log(result.label);
        }
      } else {
        recognitionCount = 0;
      }
    });
  }, 100);
});
