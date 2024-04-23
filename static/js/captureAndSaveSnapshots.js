const captureAndSaveSnapshots = async () => {
    const video = document.createElement('video');
    document.body.appendChild(video);

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });

    video.srcObject = stream;
    await video.play();

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const folderName = `snapshots/${userId}`;

    await fetch(`/create-folder?folderName=${folderName}`, {
        method: 'POST'
    });

    for (let i = 0; i < 5; i++) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async function(blob) {
            const formData = new FormData();
            formData.append('snapshot', blob, `${i + 1}.jpeg`);

            await fetch(`/save-snapshot?folderName=${folderName}`, {
                method: 'POST',
                body: formData
            });
        }, 'image/jpeg');

        await new Promise(resolve => setTimeout(resolve, 1000)); // Задержка между снимками
    }

    stream.getTracks().forEach(track => track.stop());
    document.body.removeChild(video);
};

document.getElementById('capture-snapshots').addEventListener('click', () => {
    captureAndSaveSnapshots();
});
