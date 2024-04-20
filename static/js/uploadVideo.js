const startRecordingButton = document.getElementById('start-recording');
let mediaRecorder;
let stream;

async function startRecording() {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    mediaRecorder = new MediaRecorder(stream);
    let chunks = [];

    mediaRecorder.ondataavailable = function(e) {
        chunks.push(e.data);
    };

    mediaRecorder.onstop = async function(e) {
        const blob = new Blob(chunks, { 'type' : 'video/mp4' });
        chunks = [];
        let formData = new FormData();
        formData.append('video', blob, 'recording.mp4');
        
        try {
            const response = await fetch('/upload-video', {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                console.log("Видео успешно загружено на сервер");
            } else {
                console.error("Ошибка загрузки видео на сервер");
            }
        } catch (error) {
            console.error("Ошибка при отправке видео на сервер:", error);
        }
    };

    mediaRecorder.start();
    console.log("Запись началась");
}

startRecordingButton.addEventListener('click', () => {
    startRecording();
    startRecordingButton.setAttribute("disabled", true);
    setTimeout(() => {
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
        startRecordingButton.removeAttribute("disabled");
        console.log("Запись остановлена");
    }, 30000); // Запись останавливается через 5 секунд
});