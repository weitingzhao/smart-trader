let currentIndex = -1;

function fetchAutoReminder(event) {

    const resultsContainer = document.getElementById('auto_reminder_results');
    const query = event.target.value;
    if (query.length === 0) {
        document.getElementById('auto_reminder_results').innerHTML = '';
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
        return;
    }

    fetch(`/auto_reminder/?query=${query}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';
            const regex = new RegExp(`(${query})`, 'gi');
            data.forEach((item,index) => {
                const resultItem = document.createElement('a');
                resultItem.className = 'list-group-item list-group-item-action';
                resultItem.setAttribute('data-index', index);
                resultItem.setAttribute('data-symbol', item.symbol);
                const highlightedSymbol = item.symbol.replace(regex, '<span class="highlight">$1</span>');
                const highlightedName = item.name.replace(regex, '<span class="highlight">$1</span>');
                resultItem.innerHTML = `
                <div class="result-line1">${highlightedSymbol} - ${highlightedName}</div>
                <div class="result-line2">${item.market}</div>
              `;
                resultItem.addEventListener('click', () => {
                    currentIndex = index;
                    selectResult();
                });
                resultItem.addEventListener('mouseover', () => {
                    // console.log('mouseover:', currentIndex);
                    currentIndex = index;
                    highlightResult();
                });
                resultsContainer.appendChild(resultItem);
            });
            resultsContainer.style.display = 'block';
        });
    // console.log('Match by query:', query);
    currentIndex = -1;
}

function handleKeyEvents(event) {
    if (event.key === 'ArrowDown') {
        navigateResults(1);
    } else if (event.key === 'ArrowUp') {
        navigateResults(-1);
    } else if (event.key === 'Enter') {
        selectResult();
    }
}

function navigateResults(direction) {
    const results = document.querySelectorAll('#auto_reminder_results .list-group-item');
    if (results.length === 0) return;

    currentIndex = (currentIndex + direction + results.length) % results.length;
    highlightResult();

    const selectedResult = results[currentIndex];
    const resultsContainer = document.getElementById('auto_reminder_results');
    const containerTop = resultsContainer.scrollTop;
    const containerBottom = containerTop + resultsContainer.clientHeight;
    const resultTop = selectedResult.offsetTop;
    const resultBottom = resultTop + selectedResult.clientHeight;

    if (resultTop < containerTop) {
        resultsContainer.scrollTop = resultTop;
    } else if (resultBottom > containerBottom) {
        resultsContainer.scrollTop = resultBottom - resultsContainer.clientHeight;
    }
}

function highlightResult() {
    const results = document.querySelectorAll('#auto_reminder_results .list-group-item');
    results.forEach((result, index) => {
        result.classList.toggle('active', index === currentIndex);
    });
}

function selectResult() {
    const results = document.querySelectorAll('#auto_reminder_results .list-group-item');
    if (currentIndex >= 0 && currentIndex < results.length) {
        console.log('Open Index:', currentIndex);
        const selectedResult = results[currentIndex];
        const symbol = selectedResult.getAttribute('data-symbol');
        window.location.href = `/stock/quote/profile?symbol=${symbol}`;
    }
}

document.getElementById('header_search').addEventListener('blur', function() {
  setTimeout(function() {
    document.getElementById('auto_reminder_results').style.display = 'none';
  }, 200); // Delay to allow click events on results
});

document.getElementById('header_search').addEventListener('focus', function() {
  document.getElementById('auto_reminder_results').style.display = 'block';
});