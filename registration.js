document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registrationForm");
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault(); 
        const firstName = document.getElementById("firstName").value.trim();
        const lastName = document.getElementById("lastName").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const state = document.getElementById("state").value;
        if (!firstName || !lastName || !email || !password || !state) {
            alert("❌ Please fill in all fields.");
            return;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("❌ Enter a valid email address.");
            return;
        }
        if (password.length < 8) {
            alert("❌ Password must be at least 8 characters.");
            return;
        }
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
         if (password.length === 0) {
            passwordMessage.innerText = "";
        } else if (!passwordRegex.test(password)) {
            passwordMessage.innerText =
                "❌ Password must be at least 8 characters, include 1 uppercase letter, 1 number, and 1 special character.";
            passwordMessage.style.color = "red";
        } else {
            passwordMessage.innerText = "✅ Strong password";
            passwordMessage.style.color = "green";
        }
        console.log("🔄 Sending data:", { firstName, lastName, email, state });
        try {
            const response = await fetch("http://localhost:5000/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ firstName, lastName, email, password, state }),
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                localStorage.setItem("firstName", result.firstName);
                localStorage.setItem("lastName", result.lastName);
                localStorage.setItem("email", result.email);
                localStorage.setItem("coins", result.coins);
                
                console.log("💾 Stored user data:", {
                    firstName: result.user.firstName,
                    lastName: result.lastName,
                    email: result.email,
                    coins: result.coins
                });
                
                window.location.href = "home-page.html"; 
            } else {
                alert(result.message || "❌ Registration failed!");
            }
        } catch (error) {
            console.error("Registration Error:", error);
            alert("❌ Registration failed. Please try again.");
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    loadUserData();
});

function loadUserData() {
    const firstName = localStorage.getItem("firstName");
    const lastName = localStorage.getItem("lastName");
    const email = localStorage.getItem("email");
    const coins = localStorage.getItem("coins");
    
    console.log("📋 Loading user data:", { firstName, lastName, email, coins });
    const welcomeElement = document.querySelector('[data-user-name]');
    if (welcomeElement && firstName) {
        welcomeElement.textContent = firstName;
    }
    const coinsElement = document.querySelector('[data-user-coins]');
    if (coinsElement && coins) {
        coinsElement.textContent = coins;
    }
    if (!firstName || !email) {
        console.log("⚠️ No user data found, redirecting to login");
    }
}
function updateUserInterface(userData) {
    const welcomeElement = document.querySelector('[data-user-name]');
    if (welcomeElement && userData.firstName) {
        welcomeElement.textContent = userData.firstName;
    }
    const coinsElement = document.querySelector('[data-user-coins]');
    if (coinsElement && userData.coins) {
        coinsElement.textContent = userData.coins;
    }
    
    console.log("🔄 UI updated with user data:", userData);
}