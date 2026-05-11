async function signup(event) {
  event.preventDefault();

  const username = document.getElementById("name").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    alert("Please fill all fields");
    return;
  }

  try {
    const response = await fetch("http://localhost:5000/signup", {
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

    alert(data.message);

    window.location.href = "./index.html";
  } catch (error) {
    alert("Server error");
    console.log(error);
  }
}

document.getElementById("signupForm").addEventListener("submit", signup);
