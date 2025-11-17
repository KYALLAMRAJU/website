// ---------------------------------------------------------
// 🎵 Audio Modal & Background Intro Audio Control
// ---------------------------------------------------------

const modal = document.getElementById("audioModal");
const closeModal = document.getElementById("closeModal");
const audioList = document.getElementById("audioList");
const audioPlayer = document.getElementById("audioPlayer");
const modalTitle = document.getElementById("modalTitle");
const introAudio = document.getElementById("introAudio");

// ---------------------------------------------------------
// 🪷 Dummy Audio Data (replace with your static paths)
// ---------------------------------------------------------
const audioData = {
    upanisad: [
        {title: "Day 1 – Introduction", file: "/static/audio/upanisad/day1.mp3"},
        {title: "Day 2 – Concept of Brahman", file: "/static/audio/upanisad/day2.mp3"},
    ],
    bhagavadgita: [
        {title: "Chapter 1 – Arjuna Vishada Yoga", file: "/static/audio/gita/ch1.mp3"},
        {title: "Chapter 2 – Sankhya Yoga", file: "/static/audio/gita/ch2.mp3"},
    ],
    grantha: [
        {title: "Aparokshanubhuti", file: "/static/audio/grantha/aparoksha.mp3"},
    ],
    vidyaranya: [
        {title: "Vivekachudamani Talk", file: "/static/audio/vidyaranya/viveka.mp3"},
    ],
};

// ---------------------------------------------------------
// 🎧 Handle Modal Opening (Load Audio List)
// ---------------------------------------------------------
document.querySelectorAll(".audio-card-modern").forEach((card) => {
    card.addEventListener("click", () => {
        const category = card.dataset.category;
        modalTitle.textContent = card.textContent.trim();
        audioList.innerHTML = "";

        // Fade out intro audio when modal opens
        if (introAudio && !introAudio.paused) {
            let vol = introAudio.volume;
            const fadeOut = setInterval(() => {
                if (vol > 0.02) {
                    vol -= 0.02;
                    introAudio.volume = vol;
                } else {
                    introAudio.pause();
                    introAudio.currentTime = 0;
                    clearInterval(fadeOut);
                }
            }, 80);
        }

        audioData[category]?.forEach((audio) => {
            const li = document.createElement("li");
            li.textContent = audio.title;
            li.addEventListener("click", () => {
                audioPlayer.src = audio.file;
                audioPlayer.play();
            });
            audioList.appendChild(li);
        });

        modal.classList.add("show");
    });
});

// ---------------------------------------------------------
// 🔇 Close Modal or Background Click
// ---------------------------------------------------------
closeModal.addEventListener("click", () => {
    modal.classList.remove("show");
    resumeIntroAudio();
});

window.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("show");
        resumeIntroAudio();
    }
});

// ---------------------------------------------------------
// 🔁 Resume Intro Audio (Fade Back In)
// ---------------------------------------------------------
function resumeIntroAudio() {
    if (introAudio) {
        introAudio.currentTime = 0;
        introAudio.play();
        introAudio.volume = 0;
        let v = 0;
        const fadeBack = setInterval(() => {
            if (v < 0.25) {
                v += 0.02;
                introAudio.volume = v;
            } else clearInterval(fadeBack);
        }, 150);
    }
}

// ---------------------------------------------------------
// 🌅 Background Intro Audio – Autoplay Logic
// ---------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    if (introAudio) {
        introAudio.volume = 0.15;
        const playPromise = introAudio.play();

        if (playPromise !== undefined) {
            playPromise.then(() => {
                // Smooth fade-in
                let vol = 0.05;
                const fade = setInterval(() => {
                    if (vol < 0.25) {
                        vol += 0.01;
                        introAudio.volume = vol;
                    } else clearInterval(fade);
                }, 200);
            }).catch(() => {
                // Autoplay blocked → show a “Play Background” button
                const btn = document.createElement("button");
                btn.textContent = "🔊 Play Background Audio";
                Object.assign(btn.style, {
                    position: "fixed",
                    bottom: "20px",
                    right: "20px",
                    zIndex: "9999",
                    background: "#ffc107",
                    color: "#000",
                    border: "none",
                    borderRadius: "8px",
                    padding: "10px 15px",
                    fontWeight: "600",
                    boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
                    cursor: "pointer",
                });
                document.body.appendChild(btn);
                btn.addEventListener("click", () => {
                    introAudio.volume = 0.25;
                    introAudio.play();
                    btn.remove();
                });
            });
        }
    }

    // Pause intro audio when a main audio starts
    if (audioPlayer) {
        audioPlayer.addEventListener("play", () => {
            if (introAudio && !introAudio.paused) introAudio.pause();
        });

        // Restore intro audio when playback ends
        audioPlayer.addEventListener("ended", resumeIntroAudio);
    }
});
