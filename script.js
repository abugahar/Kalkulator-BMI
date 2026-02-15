document.getElementById("bmiForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Mencegah refresh halaman

    const data = {
        nama: document.getElementById("nama").value.trim(),
        usia: document.getElementById("usia").value.trim(),
        jenis_kelamin: document.getElementById("jenis_kelamin").value,
        berat: document.getElementById("berat").value.trim(),
        tinggi: document.getElementById("tinggi").value.trim(),
        aktivitas: document.getElementById("aktivitas").value,
        email: document.getElementById("email").value.trim()
    };

    fetch("/hitung_bmi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        let hasilDiv = document.getElementById("hasil");
        if (data.error) {
            hasilDiv.style.color = "red";
            hasilDiv.innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
        } else {
            hasilDiv.style.color = "black";
            hasilDiv.style.backgroundColor = "#ffebcc";
            hasilDiv.innerHTML = `<p><strong>BMI:</strong> ${data.bmi}</p>
                                  <p><strong>Rekomendasi:</strong> ${data.rekomendasi}</p>`;
        }
        hasilDiv.style.display = "block";
    })
    .catch(error => {
        console.error("Error:", error);
        let hasilDiv = document.getElementById("hasil");
        hasilDiv.style.color = "red";
        hasilDiv.innerHTML = `<p><strong>Error:</strong> Terjadi kesalahan saat menghitung BMI.</p>`;
        hasilDiv.style.display = "block";
    });
});
