document.addEventListener("DOMContentLoaded", function () { 
    const loginForm = document.getElementById("loginForm"); // Target the form

    if (!loginForm) {
        console.error("❌ loginForm not found!");
        return;
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent page refresh

        const emailInput = document.querySelector(".email1");
        const passwordInput = document.querySelector(".password1");

        if (!emailInput || !passwordInput) {
            console.error("❌ Email or password input not found!");
            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            alert("❌ Please enter both email and password.");
            return;
        }

        try {
            const response = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const result = await response.json();
            console.log("🔹 Server Response:", result); // Debugging log

            if (!response.ok) {
                alert(result.message || "❌ Login failed. Please try again.");
                return;
            }

            // Ensure firstName & coins exist in response
            const firstName = result.firstName || "Guest"; // Default name if missing
            const coins = result.coins !== undefined ? result.coins : 0; // Default 0 coins if missing

            // ✅ Store user details
            localStorage.setItem("email", email);
            localStorage.setItem("firstName", firstName);
            localStorage.setItem("coins", coins); // Store user coins for leaderboard

            console.log("✅ Stored Data:", { email, firstName, coins }); // Debugging log

            // Redirect after successful login
            window.location.href = "home-page.html"; 

        } catch (error) {
            console.error("❌ Login Error:", error);
            alert("❌ Login failed. Please try again.");
        }
    });
});
