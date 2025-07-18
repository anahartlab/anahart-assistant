<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Assistant</title>
</head>
<body>
    <h1>Assistant</h1>
    <div>
        <textarea id="userInput" rows="4" cols="50"></textarea><br/>
        <button id="sendBtn">Send</button>
    </div>
    <div id="response"></div>

    <script>
        const sendBtn = document.getElementById("sendBtn");
        const userInput = document.getElementById("userInput");
        const responseElement = document.getElementById("response");

        sendBtn.addEventListener("click", async () => {
            const message = userInput.value;
            const response = await fetch("/assistant", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            responseElement.innerHTML = data.reply;
        });
    </script>
</body>
</html>