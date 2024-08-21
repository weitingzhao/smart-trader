function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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
                const listItem = document.createElement('li');
                listItem.className = 'mb-2';
                const linkitem = document.createElement('a');
                linkitem.className = 'dropdown-item border-radius-md';
                linkitem.setAttribute('data-index', index);
                linkitem.setAttribute('data-symbol', item.symbol);
                const highlightedSymbol = item.symbol.replace(regex, '<span class="highlight">$1</span>');
                const highlightedName = item.name.replace(regex, '<span class="highlight">$1</span>');
                linkitem.innerHTML = `
                <div class="result-line1">${highlightedSymbol} - ${highlightedName}</div>
                <div class="result-line2">${item.market}</div>
              `;
                linkitem.addEventListener('click', () => {
                    currentIndex = index;
                    selectResult();
                });
                linkitem.addEventListener('mouseover', () => {
                    // console.log('mouseover:', currentIndex);
                    currentIndex = index;
                    highlightResult();
                });
                listItem.appendChild(linkitem);
                resultsContainer.appendChild(listItem);
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
    const results = document.querySelectorAll('#auto_reminder_results .mb-2 .dropdown-item');
    console.log('Results:', results.length);
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
    const results = document.querySelectorAll('#auto_reminder_results .mb-2 .dropdown-item');
    results.forEach((result, index) => {
        if (index === currentIndex) {
            result.classList.add('bg-dark');
            result.classList.add('text-white');
        } else {
            result.classList.remove('bg-dark');
            result.classList.remove('text-white');
        }
    });
}

function selectResult() {
    const results = document.querySelectorAll('#auto_reminder_results .mb-2 .dropdown-item');
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
    const notificationMenu = document.getElementById('notificationMenu');
    const notificationCount = document.getElementById('notificationCount');
    const max_notifications = 10;
    let notificationQueue={};
    let unread_count = 0;
    let read_all_link = null;
    notificationMenu.innerHTML = ''; // Clear existing notifications

    // Toggle dropdown visibility
    notificationButton.addEventListener('click', function(event) {
        notificationMenu.classList.toggle('show');
        // Toggle aria-expanded attribute
        let expanded = notificationMenu.classList.contains('show');
        this.setAttribute('aria-expanded', expanded);
    });

    // Close dropdown if clicking outside
    document.addEventListener('click', function(event) {
        if (!notificationMenu.contains(event.target) && !notificationButton.contains(event.target)) {
            notificationMenu.classList.remove('show');
            notificationButton.setAttribute('aria-expanded', 'false');
        }
    });

    // Prevent closing dropdown when clicking inside the menu
    notificationMenu.addEventListener('click', function(event) {
        event.stopPropagation(); // Prevents the click from bubbling up to the document
    });


    function generateNotificationPanel(notification) {
        const listItem = document.createElement('li');
        listItem.className = 'mb-2';
        const link = document.createElement('a');
        link.className = 'dropdown-item border-radius-md';
        link.href = 'javascript:;';
        const div1 = document.createElement('div');
        div1.className = 'd-flex py-1';
        const div2 = document.createElement('div');
        div2.className = 'my-auto';
        const img = document.createElement('img');
        img.src = "/static/assets/img/illustrations/chat.png" //notification.image;
        img.className = 'avatar avatar-sm me-3';
        img.alt = 'user image';
        // Set background color based on notification level
        switch (notification.level) {
            case 'success':
                img.classList.add('bg-gradient-success');
                break;
            case 'info':
                img.classList.add('bg-gradient-info');
                break;
            case 'warning':
                img.classList.add('bg-gradient-warning');
                break;
            case 'error':
                img.classList.add('bg-gradient-danger');
                break;
            default:
                img.classList.add('bg-gradient-info'); // Default to info if level is not recognized
                break;
        }

        const div3 = document.createElement('div');
        div3.className = 'd-flex flex-column justify-content-center';
        const h6 = document.createElement('h6');
        h6.className = 'text-sm font-weight-normal mb-1';
        h6.innerHTML = `<span class="font-weight-bold">${notification.verb}</span> by ${notification.actor}`;
        const p = document.createElement('p');
        p.className = 'text-xs text-secondary mb-0';
        p.innerHTML = `<i class="fa fa-clock me-1"></i>${notification.timestamp}`;

        const closeButtonWrapper = document.createElement('div');
        closeButtonWrapper.className = 'close-button-wrapper d-flex justify-content-center align-items-center';
        closeButtonWrapper.style.width = '24px';
        closeButtonWrapper.style.height = '24px';
        closeButtonWrapper.style.cursor = 'pointer';

        // Add close button
        const closeButton = document.createElement('i');
        closeButton.className = 'fas fa-times text-md ms-3 cursor-pointer';
        closeButton.style.margin = 'auto 0'; // Center the button vertically
        closeButton.addEventListener('click', function() {
            markAsRead(notification.slug, listItem);
        });

        closeButtonWrapper.appendChild(closeButton);

        div3.appendChild(h6);
        div3.appendChild(p);

        div2.appendChild(img);

        div1.appendChild(div2);
        div1.appendChild(div3);
        div1.appendChild(closeButtonWrapper);

        link.appendChild(div1);

        listItem.appendChild(link);
        notificationMenu.appendChild(listItem);

        // Add to queue
        notificationQueue[notification.slug] = notification;
    }

    function markAsRead(slug, listItem) {
        fetch(`/inbox/notifications/mark-as-read/${slug}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }
        })
            .then(response => {
                if (response.ok) {
                    delete notificationQueue[slug]; // Remove from queue
                    listItem.remove(); // Remove from panel
                    fetchNotifications(); // Refresh the notification list
                } else {
                    console.error('Failed to mark notification as read');
                }
            })
            .catch(error => {
                console.error('Error marking notification as read:', error);
            });
    }

    function markAllAsRead() {
        fetch('/inbox/notifications/mark-all-as-read/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')}
        })
            .then(response => {
                if (response.ok) {
                    notificationQueue = {}; // Clear the queue
                    notificationMenu.innerHTML = ''; // Clear existing notifications
                    fetchNotifications(); // Refresh the notification list
                } else {
                    console.error('Failed to mark all notifications as read');
                }
            })
            .catch(error => {
                console.error('Error marking all notifications as read:', error);
            });
    }

    function fetchNotifications() {
        fetch('/inbox/notifications/api/unread_list/')
            .then(response => response.json())
            .then(data => {
                // Update notification count
                 unread_count = data.unread_count;
                if (unread_count > 0) {
                    notificationCount.textContent = unread_count > 99 ? '99+' : unread_count;
                    notificationCount.style.display = 'block';
                    notificationMenu.style.maxHeight = "none"; // adjust to max-height
                    notificationMenu.style.overflowY = 'auto';

                    // Add "Read All Link"
                    if (read_all_link == null) {
                        read_all_link = document.createElement('a');
                        read_all_link.href = 'javascript:;';
                        read_all_link.className = 'dropdown-item text-center';
                        read_all_link.textContent = 'Read All';
                        read_all_link.addEventListener('click', markAllAsRead);
                        notificationMenu.appendChild(read_all_link);
                    }

                    // generate notification panel
                    if (data.unread_list) {
                        // Update queue with new notifications
                        data.unread_list.forEach((notification, index) => {
                            if (!notificationQueue[notification.slug] && Object.keys(notificationQueue).length <= max_notifications) {
                                generateNotificationPanel(notification);
                            }
                        });
                    } else {
                        console.error('Failed to fetch notifications:', data.error);
                    }

                } else {
                    //Remove "Read All Link"
                    if(read_all_link != null)
                        read_all_link.remove();
                    read_all_link = null;

                    notificationCount.textContent = 0;
                    notificationCount.style.display = 'none';
                    notificationMenu.style.maxHeight = '55px'; // adjust to original max-height
                    notificationMenu.style.overflowY = 'none';

                    // Add message if no notifications
                    const noNotificationsMessage = document.createElement('p');
                    noNotificationsMessage.textContent = 'no more message';
                    notificationMenu.appendChild(noNotificationsMessage);
                }

            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
            });
    }
    fetchNotifications();
});