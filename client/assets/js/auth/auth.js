async function login(event) {
  event.preventDefault();

  const username = document.getElementById("name").value.trim();

  const password = document.getElementById("password").value;

  if (!username || !password) {
    alert("Please enter username and password.");

    return;
  }

  try {
    const response = await fetch("https://ai-educator.onrender.com/login", {
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
    console.error(error);

    alert("Server error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  if (form) {
    form.addEventListener("submit", login);
  }
});
