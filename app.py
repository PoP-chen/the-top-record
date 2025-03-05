<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>單字卡練習</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
        h1 { color: #333; }
        input, button { margin: 5px; padding: 10px; font-size: 16px; }
        .card-container { display: flex; flex-wrap: wrap; justify-content: center; }
        .card { width: 200px; height: 100px; margin: 10px; background: #f8f9fa; 
                border: 1px solid #ddd; display: flex; align-items: center; 
                justify-content: center; font-size: 20px; cursor: pointer; 
                transition: transform 0.3s; }
        .card:hover { transform: scale(1.05); }
        .flipped { background: #007bff; color: white; }
        .delete-btn { margin-top: 5px; padding: 5px 10px; font-size: 14px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>單字卡練習</h1>
    
    <input type="text" id="english" placeholder="輸入英文單字">
    <input type="text" id="chinese" placeholder="輸入中文翻譯">
    <button onclick="addCard()">新增單字卡</button>

    <div class="card-container" id="cardContainer"></div>

    <script>
        let words = JSON.parse(localStorage.getItem("words")) || [];

        function renderCards() {
            const container = document.getElementById("cardContainer");
            container.innerHTML = "";
            words.forEach((word, index) => {
                const card = document.createElement("div");
                card.className = "card";
                card.innerText = word.english;
                card.onclick = () => {
                    card.innerText = card.innerText === word.english ? word.chinese : word.english;
                    card.classList.toggle("flipped");
                };

                const deleteBtn = document.createElement("button");
                deleteBtn.className = "delete-btn";
                deleteBtn.innerText = "刪除";
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    words.splice(index, 1);
                    localStorage.setItem("words", JSON.stringify(words));
                    renderCards();
                };

                const cardWrapper = document.createElement("div");
                cardWrapper.appendChild(card);
                cardWrapper.appendChild(deleteBtn);
                container.appendChild(cardWrapper);
            });
        }

        function addCard() {
            const english = document.getElementById("english").value.trim();
            const chinese = document.getElementById("chinese").value.trim();
            if (english && chinese) {
                words.push({ english, chinese });
                localStorage.setItem("words", JSON.stringify(words));
                document.getElementById("english").value = "";
                document.getElementById("chinese").value = "";
                renderCards();
            } else {
                alert("請輸入完整的單字和翻譯！");
            }
        }

        renderCards();
    </script>
</body>
</html>