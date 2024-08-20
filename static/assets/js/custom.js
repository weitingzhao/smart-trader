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
        window.location.href = `/stock/quote/${symbol}`;
    }
}

document.getElementById('header_search').addEventListener('input', fetchAutoReminder);
document.getElementById('header_search').addEventListener('keydown', handleKeyEvents);
document.getElementById('header_search').addEventListener('blur', function() {
  setTimeout(function() {
    document.getElementById('auto_reminder_results').style.display = 'none';
  }, 200); // Delay to allow click events on results
});
document.getElementById('header_search').addEventListener('focus', function() {
  document.getElementById('auto_reminder_results').style.display = 'block';
});

// Create a container for the toasts if it doesn't exist
let toastContainer = document.getElementById('toast-container');
if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'position-fixed bottom-1 end-1 z-index-2';
    document.body.appendChild(toastContainer);
}

//Notification
function showNotification(level, title, content, timeAgo = 'just now') {
    // Create the toast container
    const toast = document.createElement('div');
    toast.className = `toast fade hide p-2 mt-2 bg-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Declare the toast header
    const toastHeader = document.createElement('div');
    // Declare title
    const titleSpan = document.createElement('span');
    titleSpan.innerText = title;
    // Declare time ago
    const time = document.createElement('small');
    time.innerText = timeAgo;
    // Declare close button
    const closeButton = document.createElement('i');
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    // Declare horizontal line
    const hr = document.createElement('hr');
    // Declare toast body
    const toastBody = document.createElement('div');
    toastBody.innerText = content;

    switch (level) {
        case 'info':
            toastHeader.className = 'toast-header bg-transparent border-0';
            titleSpan.className = 'me-auto text-white font-weight-bold';
            time.className = 'text-white';
            closeButton.className = 'fas fa-times text-md text-white ms-3 cursor-pointer';

            hr.className = 'horizontal light m-0';
            toastBody.className = 'toast-body text-white';
            break;
        default:
            toastHeader.className = 'toast-header border-0';
            titleSpan.className = 'me-auto font-weight-bold';
            time.className = 'text-body';
            closeButton.className = 'fas fa-times text-md ms-3 cursor-pointer';

            hr.className = 'horizontal dark m-0';
            toastBody.className = 'toast-body';
            break;
    }
    // Add icon based on level
    const icon = document.createElement('i');
    switch (level) {
        case 'success':
            icon.className = 'ni ni-check-bold text-success me-2';
            break;
        case 'info':
            icon.className = 'ni ni-bell-55 text-white me-2';
            toast.classList.add('bg-gradient-info');
            break;
        case 'warning':
            icon.className = 'ni ni-spaceship text-warning me-2';
            break;
        case 'error':
            icon.className = 'ni ni-notification-70 text-danger me-2';
            break;
        default:
            icon.className = 'ni ni-bell-55 text-white me-2';
            break;
    }
    toastHeader.appendChild(icon);
    toastHeader.appendChild(titleSpan);
    toastHeader.appendChild(time);
    toastHeader.appendChild(closeButton);
    toast.appendChild(toastHeader);
    toast.appendChild(hr);
    toast.appendChild(toastBody);

    // Append toast to the toast container
    toastContainer.appendChild(toast);

    // Show the toast
    const bootstrapToast = new bootstrap.Toast(toast);
    bootstrapToast.show();

    // Remove the toast after it hides
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}
//showNotification('success', 'Soft UI Dashboard', 'Hello, world! This is a notification message.', '11 mins ago');
// showNotification('info', 'Soft UI Dashboard', 'Hello, world! This is an info message.', '11 mins ago');
// showNotification('warning', 'Soft UI Dashboard', 'Hello, world! This is a warning message.', '11 mins ago');
// showNotification('danger', 'Soft UI Dashboard', 'Hello, world! This is a danger message.', '11 mins ago');

document.addEventListener('DOMContentLoaded', function() {
    const notificationButton = document.getElementById('notificationButton');
    const notificationPanel = document.getElementById('notificationPanel');
    //
    // notificationButton.addEventListener('click', function () {
    //     if (notificationPanel.style.display === 'none' || notificationPanel.style.display === '') {
    //         notificationPanel.style.display = 'block';
    //     } else {
    //         notificationPanel.style.display = 'none';
    //     }
    // });

    function generateNotificationPanel(notifications) {
        notifications.forEach(notification => {
            const listItem = document.createElement('li');
            listItem.className = 'mb-2';
            const link = document.createElement('a');
            link.className = 'dropdown-item border-radius-md';
            link.href = 'javascript:;';
            const div1 = document.createElement('div');
            div1.className = 'd-flex py-1';
            const div2 = document.createElement('div');
            div2.className = 'my-auto';
            // const img = document.createElement('img');
            // img.src = notification.image;
            // img.className = 'avatar avatar-sm me-3';
            // img.alt = 'user image';

            const div3 = document.createElement('div');
            div3.className = 'd-flex flex-column justify-content-center';
            const h6 = document.createElement('h6');
            h6.className = 'text-sm font-weight-normal mb-1';
            h6.innerHTML = `<span class="font-weight-bold">${notification.verb}</span> by ${notification.actor}`;
            const p = document.createElement('p');
            p.className = 'text-xs text-secondary mb-0';
            p.innerHTML = `<i class="fa fa-clock me-1"></i>${notification.timestamp}`;

            div3.appendChild(h6);
            div3.appendChild(p);

            // div2.appendChild(img);

            div1.appendChild(div2);
            div1.appendChild(div3);

            link.appendChild(div1);

            listItem.appendChild(link);
            notificationPanel.appendChild(listItem);
        });
    }
    function fetchNotifications() {
        fetch('/inbox/notifications/api/all_list/')
            .then(response => response.json())
            .then(data => {
                notificationPanel.innerHTML = "";
                // console.log("=>"+notificationPanel.innerHTML)
                notificationPanel.innerHTML = ''; // Clear existing notifications
                if (data.all_list) {
                    generateNotificationPanel(data.all_list);
                } else {
                    console.error('Failed to fetch notifications:', data.error);
                }
                // console.log("after=>"+notificationPanel.innerHTML);
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
            });
        // console.log("init=>"+notificationPanel.innerHTML+" end")
    }
    fetchNotifications();
});