async function login(event) {
  event.preventDefault();

  const username = document.getElementById("name").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    alert("Please enter username and password.");
    return;
  }

  try {
    const response = await fetch("https://ai-educator.onrender.com", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name: username,
        password: password,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("studentName", username);

      alert(data.message);

      window.location.href = "dashboard.html";
    } else {
      alert(data.message);
    }
  } catch (error) {
    alert("Server error");
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.querySelector("form");

  if (loginForm) {
    loginForm.addEventListener("submit", login);
  }
});
