const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const statusBox = document.getElementById("status");
const tableBody = document.querySelector("#table tbody");

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => (video.srcObject = stream));

function startAttendance() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  ctx.drawImage(video, 0, 0);
  const imageData = canvas.toDataURL("image/jpeg");

  fetch("http://127.0.0.1:5000/attendance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData }),
  })
    .then((res) => res.json())
    .then((data) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (data.status === "success") {
        drawCircle("green");
        statusBox.className = "status success";
        statusBox.innerText =
          "ĐÃ ĐIỂM DANH THÀNH CÔNG (" + data.accuracy + "%)";
      } else {
        drawCircle("red");
        statusBox.className = "status fail";
        statusBox.innerText = "ĐIỂM DANH KHÔNG THÀNH CÔNG";
      }
    });
}

function drawCircle(color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, 100, 0, Math.PI * 2);
  ctx.stroke();
}

function loadToday() {
  fetch("http://127.0.0.1:5000/today")
    .then((res) => res.json())
    .then((data) => {
      tableBody.innerHTML = "";
      data.forEach((row) => {
        tableBody.innerHTML += `
                <tr>
                    <td><img src="../Backend/storage/${row.image}"></td>
                    <td>${row.name}</td>
                    <td>${row.class}</td>
                    <td>${row.date}</td>
                    <td>${row.time}</td>
                </tr>`;
      });
    });
}
