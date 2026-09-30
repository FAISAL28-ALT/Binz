document.addEventListener("DOMContentLoaded", function () {
    const usernameElement = document.getElementById("username");
    const bookBtn = document.getElementById("bookBtn");
    const phoneNumberInput = document.getElementById("phoneNumber");

    const storedName = localStorage.getItem("firstName");
    const storedEmail = localStorage.getItem("email");

    if (storedName && storedName !== "undefined" && storedName !== "null") {
        usernameElement.textContent = storedName;
    } else {
        usernameElement.textContent = "Guest";
    }

    bookBtn.addEventListener("click", function () {
        const phoneNumber = phoneNumberInput.value.trim();

        if (!phoneNumber || phoneNumber.length !== 10) {
            alert("⚠️ Please enter a valid 10-digit phone number!");
            return;
        }

        fetch("http://localhost:5000/sendSMS", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ phoneNumber: phoneNumber }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error("❌ Error:", error);
            alert("❌ Something went wrong. Try again!");
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const coinElement = document.getElementById("coin");
    if (!coinElement) return;

    let coins = localStorage.getItem("coins") || 0;
    coinElement.textContent = coins;
});

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch("http://localhost:5000/leaderboard");
        const result = await response.json();

        if (!response.ok) {
            console.error("❌ Failed to fetch leaderboard:", result.message);
            return;
        }

        const leaderboard = result.leaderboard;
        if (!leaderboard || leaderboard.length === 0) return;

        if (leaderboard[0]) {
            document.getElementById("first-name").textContent = leaderboard[0].firstName;
            document.getElementById("first-id").textContent = leaderboard[0]._id;
            document.getElementById("first-coins").textContent = leaderboard[0].coins;
        }

        if (leaderboard[1]) {
            document.getElementById("second-name").textContent = leaderboard[1].firstName;
            document.getElementById("second-id").textContent = leaderboard[1]._id;
            document.querySelector(".second-coins").textContent = leaderboard[1].coins;
        }

        if (leaderboard[2]) {
            document.getElementById("third-name").textContent = leaderboard[2].firstName;
            document.getElementById("third-id").textContent = leaderboard[2]._id;
            document.getElementById("third-coins").textContent = leaderboard[2].coins;
        }

    } catch (error) {
        console.error("❌ Error fetching leaderboard:", error);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chat-toggle").addEventListener("click", function () {
        document.getElementById("chat-container").classList.toggle("hidden");
    });

    document.getElementById("close-chat").addEventListener("click", function () {
        document.getElementById("chat-container").classList.add("hidden");
    });
});

function showSection(section) {
    let content = document.getElementById("content-area");
    content.style.display = "block";

    if (section === "about") {
        content.innerHTML = `
            <h3>About Us</h3>
            <p>Welcome to Z-Chat, your AI-powered support assistant designed for seamless and efficient customer service.</p>
        `;
    } else if (section === "schedule") {
        let slots = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"];
        let options = slots.map(slot => `<option value="${slot}">${slot}</option>`).join("");

        content.innerHTML = `
            <h3>Schedule a Service</h3>
            <p>Select a time slot:</p>
            <select id="schedule-time">${options}</select>
            <p id="confirmation-message" style="display:none; color: green; font-weight: bold;"></p>
        `;
    } else if (section === "contact") {
        content.innerHTML = `
            <h3>Contact Us</h3>
            <p>Email: <a href="mailto:support@bin-z.com">support@bin-z.com</a></p>
            <p>Phone: 9696822349</p>
        `;
    } else if (section === "ewaste") {
        content.innerHTML = `
            <button id="raise-ticket-btn" class="ticket-btn" onclick="window.location.href='test.html';">Raise Your Ticket</button>
        `;
    }
}

// Final Video Upload Button Handler
document.addEventListener("DOMContentLoaded", function () {
    const uploadBtn = document.getElementById('uploadBtn');
    const statusDiv = document.getElementById('status');
    const walletDiv = document.getElementById('wallet');

    let wallet = 0;
    const usedEmails = new Set();
    const uploadedVideos = new Set();

    uploadBtn.addEventListener('click', () => {
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const videoInput = document.getElementById('video');
        const video = videoInput.files[0];

        if (!name || !email || !video) {
            alert('Please fill in all fields and upload a video.');
            return;
        }

        const videoKey = `${video.name}-${video.size}-${video.lastModified}`;

        if (usedEmails.has(email)) {
            statusDiv.innerText = "❌ This email has already been used.";
            return;
        }

        if (uploadedVideos.has(videoKey)) {
            statusDiv.innerText = "❌ This video has already been uploaded.";
            return;
        }

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="loader"></span> Uploading...';
        statusDiv.innerText = 'Uploading video...';

        setTimeout(() => {
            statusDiv.innerText = 'Processing video....... Please wait few seconds.';

            setTimeout(() => {
                const coins = Math.floor(Math.random() * 10) + 1;
                wallet += coins;
                walletDiv.innerText = `Wallet: ${wallet} Z Coins`;
                statusDiv.innerText = `🎉 Success! ${coins} Z Coins added to your wallet.`;

                usedEmails.add(email);
                uploadedVideos.add(videoKey);

                uploadBtn.disabled = false;
                uploadBtn.innerText = 'Upload Video';
            }, 30000);

        }, 2000);
    });
});

function redirectToPage(url) {
    window.location.href = url;
}

window.addEventListener("load", function () {
    const usernameElement = document.getElementById("username");
    if (localStorage.getItem("firstName")) {
        usernameElement.textContent = localStorage.getItem("firstName");
    }
});
