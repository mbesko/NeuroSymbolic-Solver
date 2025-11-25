async function solve() {
    const taskInput = document.getElementById('taskInput');
    const input = taskInput.value;
    
    if (!input.trim()) {
        alert("Пожалуйста, введите текст задачи!");
        return;
    }

    // --- 1. Подготовка UI (Режим загрузки) ---
    const btn = document.getElementById('solveBtn');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btnText');
    
    // Блокируем кнопку
    btn.disabled = true;
    btn.classList.add('opacity-70', 'cursor-not-allowed');
    spinner.classList.remove('hidden');
    btnText.innerText = "ДУМАЮ...";
    
    // Сбрасываем старые результаты
    document.getElementById('statusBanner').className = 'hidden';
    
    setLoadingState('formalOutput', '🤖 Формализую задачу...');
    setLoadingState('logOutput', '⚙️ Запускаю движок резолюций...');
    setLoadingState('explainOutput', '🎓 Пишу объяснение...');

    try {
        // --- 2. Отправка запроса на сервер ---
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: input })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Ошибка сервера");
        }

        const data = await response.json();

        // --- 3. Вывод: Формализация (JSON) ---
        const formalBox = document.getElementById('formalOutput');
        try {
            // Пытаемся распарсить JSON строку, чтобы красиво отформатировать
            const jsonObj = JSON.parse(data.formalization);
            formalBox.innerHTML = `<pre class="text-green-400 font-mono text-xs">${syntaxHighlight(jsonObj)}</pre>`;
        } catch (e) {
            // Если пришел сырой текст (fallback)
            formalBox.innerText = data.formalization;
            formalBox.classList.remove('text-slate-500', 'italic');
            formalBox.classList.add('text-green-400');
        }

        // --- 4. Вывод: Лог движка ---
        const logBox = document.getElementById('logOutput');
        // Соединяем массив строк в один текст
        logBox.innerText = data.logs.join('\n');
        logBox.classList.remove('text-slate-500', 'italic');
        logBox.classList.add('text-slate-300');
        
        // Автопрокрутка лога вниз
        logBox.scrollTop = logBox.scrollHeight;

        // --- 5. Вывод: Объяснение (Markdown) ---
        const explainBox = document.getElementById('explainOutput');
        // Используем библиотеку marked для рендеринга Markdown в HTML
        explainBox.innerHTML = marked.parse(data.explanation);
        explainBox.classList.remove('flex', 'items-center', 'justify-center'); // Убираем центрирование лоадера

        // --- 6. Статус бар (Успех/Неудача) ---
        const banner = document.getElementById('statusBanner');
        banner.classList.remove('hidden');
        
        if (data.status) {
            banner.className = "p-4 rounded-lg font-bold text-center text-lg bg-green-900/40 text-green-400 border border-green-500/50 shadow-[0_0_15px_rgba(74,222,128,0.2)] transition-all duration-500";
            banner.innerHTML = "✅ ПРОТИВОРЕЧИЕ НАЙДЕНО — ТЕОРЕМА ДОКАЗАНА";
        } else {
            banner.className = "p-4 rounded-lg font-bold text-center text-lg bg-red-900/40 text-red-400 border border-red-500/50 shadow-[0_0_15px_rgba(248,113,113,0.2)] transition-all duration-500";
            banner.innerHTML = "❌ ПРОТИВОРЕЧИЕ НЕ НАЙДЕНО";
        }

    } catch (error) {
        alert("Произошла ошибка: " + error.message);
        resetOutputsOnError();
    } finally {
        // --- 7. Возвращаем кнопку в исходное состояние ---
        btn.disabled = false;
        btn.classList.remove('opacity-70', 'cursor-not-allowed');
        spinner.classList.add('hidden');
        btnText.innerText = "ЗАПУСТИТЬ РЕШАТЕЛЬ";
    }
}

// Вспомогательная функция для установки статуса "Загрузка..." в блоках
function setLoadingState(elementId, text) {
    const el = document.getElementById(elementId);
    el.innerHTML = `
        <div class="flex items-center gap-2 text-slate-500 italic animate-pulse">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            ${text}
        </div>
    `;
}

function resetOutputsOnError() {
    document.getElementById('formalOutput').innerText = "Ожидание...";
    document.getElementById('logOutput').innerText = "Ожидание...";
    document.getElementById('explainOutput').innerText = "Ожидание...";
}

// Функция для подсветки синтаксиса JSON (делает красиво)
function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'text-orange-300'; // number
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'text-blue-300'; // key
            } else {
                cls = 'text-green-300'; // string
            }
        } else if (/true|false/.test(match)) {
            cls = 'text-purple-300'; // boolean
        } else if (/null/.test(match)) {
            cls = 'text-gray-400'; // null
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}