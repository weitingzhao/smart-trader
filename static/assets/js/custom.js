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

////////////////////////////////Symbol Reminder/////////////////////////////////////
let currentIndex = -1;
let currentPortfolioIndex = -1;
document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the value of the hidden input element
    const hiddenInput = document.getElementById('currentPortfolioIndex');
    if (hiddenInput) {
        currentPortfolioIndex = hiddenInput.value;
    }
});


function symbolSearchAutoReminder(event, reminder) {
    const resultsContainer = document.getElementById(reminder);
    const query = event.target.value;
    if (query.length === 0) {
        document.getElementById(reminder).innerHTML = '';
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
                    selectResult(reminder);
                });
                linkitem.addEventListener('mouseover', () => {
                    // console.log('mouseover:', currentIndex);
                    currentIndex = index;
                    highlightResult(reminder);
                });
                listItem.appendChild(linkitem);
                resultsContainer.appendChild(listItem);
            });
            resultsContainer.style.display = 'block';
        });
    // console.log('Match by query:', query);
    currentIndex = -1;
}

function symbolSearchKeyDown(event, reminder) {
    if (event.key === 'ArrowDown') {
        navigateResults(1, reminder);
    } else if (event.key === 'ArrowUp') {
        navigateResults(-1, reminder);
    } else if (event.key === 'Enter') {
        selectResult(reminder);
    }
}

function navigateResults(direction, reminder) {
    const results = document.querySelectorAll(`#${reminder} .mb-2 .dropdown-item`);
    console.log('Results:', results.length+" currentPortfolioIndex=> "+currentPortfolioIndex);
    if (results.length === 0) return;

    currentIndex = (currentIndex + direction + results.length) % results.length;
    highlightResult(reminder);

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

function highlightResult(reminder) {
    const results = document.querySelectorAll(`#${reminder} .mb-2 .dropdown-item`);
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

function selectResult(reminder) {
    const symbol = getSelectResult(reminder)
    if (reminder === 'auto_reminder_results') {
        window.location.href = `/stock/quote/${symbol}`;
    }else if (reminder === 'symbol_auto_reminder_results') {
        // Send AJAX request to add portfolio item
        fetch(`/portfolio/${currentPortfolioIndex}/add_item/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ symbol: symbol })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the UI to reflect the added item
                alert('Item added to portfolio successfully!');
                // Optionally, you can refresh the portfolio list or update the UI dynamically
            } else {
                alert('Failed to add item to portfolio.');
            }
        })
        .catch(error => {
            console.error('Error adding item to portfolio:', error);
            alert('An error occurred while adding the item to the portfolio.');
        });
    }
}

function getSelectResult(reminder){
    const results = document.querySelectorAll(`#${reminder} .mb-2 .dropdown-item`);
    if (currentIndex >= 0 && currentIndex < results.length) {
        const selectedResult = results[currentIndex];
        return selectedResult.getAttribute('data-symbol');
    }
}


function symbolSearchBlur(reminder) {
    setTimeout(function () {
        document.getElementById(reminder).style.display = 'none';
    }, 200); // Delay to allow click events on results
}

function symbolFocus(reminder) {
    document.getElementById(reminder).style.display = 'block';
}


////////////////////////////////Notification/////////////////////////////////////
// Create a container for the toasts if it doesn't exist
let toastContainer = document.getElementById('toast-container');
if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'position-fixed bottom-1 end-1 z-index-2';
    document.body.appendChild(toastContainer);
}

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
    toastBody.innerHTML = content

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
        const formattedTimestamp = new Date(notification.timestamp).toLocaleString('en-US').replace(',', '');
        p.innerHTML = `<i class="fa fa-clock me-1"></i>${formattedTimestamp}  <span class="text-xs text-dark">${notification.description}</span>`;

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

function showFileView(fileName) {
    const fileViewModal = document.getElementById('file-view');
    const filePathElement = document.getElementById('file-path');
    const fileContentElement = document.getElementById('file_content');
    const fileDownloadElement = document.getElementById('file-download');

    fetch(`/tasks_logs?file=${encodeURIComponent(fileName)}`)
        .then(response => response.text())
        .then(data => {
            filePathElement.textContent = fileName;
            fileContentElement.textContent = data;
            fileDownloadElement.href = `/tasks_logs?file=${encodeURIComponent(fileName)}`;
            const modal = new bootstrap.Modal(fileViewModal);
            modal.show();
        })
        .catch(error => {
            fileContentElement.textContent = 'Error loading file';
            const modal = new bootstrap.Modal(fileViewModal);
            modal.show();
        });
}

////////////////////////////////Celery Task/////////////////////////////////////
function call_celery_task(task, task_name, args) {
    console.log(args)
    fetch(`celery_task/${task}/${args}`)
        .then(response => response.json())
        .then(data => {
            const currentTime = new Date().toLocaleTimeString();
            if (data.success) {
                showNotification(
                    'success', task_name,
                    `Task satus: <b>${data.status}</b> <br>id: <b>${data.task_id}</b>`,
                    data.on);
            } else {
                showNotification('error', task_name, data.error, currentTime);
            }
        })
        .catch(error => {
            showNotification('error', task_name, error, new Date().toLocaleTimeString());
        });
}

function retryTask(taskId) {
    fetch(`tasks/retry/${taskId}`)
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            console.error('Failed to retry task:', taskId, response);
            alert(`Failed to retry task: ${taskId}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Failed to retry task: ${taskId}`);
    });
}

////////////////////////////////Format Date/////////////////////////////////////
function formatToDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

////////////////////////////////Dropdown Exchange/////////////////////////
async function renderDropdown(
    category, type,
    allow_multiple= false,
    need_all= true,
    need_none= true,
    value=null,
    default_value = null
){
    const dropdown = document.getElementById(`dropdown_${category}_${type}`);
    if (!dropdown) {
        console.error(`Dropdown element with id "dropdown_${category}_${type}" not found.`);
        return;
    }
    // Clear existing content
    dropdown.innerHTML = '';
    // Decode the type to replace %20 with space
    const decodedType = decodeURIComponent(type);
    const anchor_id = `navbar_dropdown_menu_${category}_${type}`;

    // Create the anchor element
    const anchor = document.createElement('a');
    anchor.href = 'javascript:;';
    anchor.className = 'btn bg-gradient-light dropdown-toggle w-100';
    anchor.style.height = '50px';
    anchor.setAttribute('data-bs-toggle', 'dropdown');
    anchor.id = anchor_id;

    // Create the dropdown name  & selected option display element
    const dropdownName = document.createElement('div');
    dropdownName.className = 'dropdown-name text-lg';
    dropdownName.textContent = decodedType;
    const selectedOptionDisplay = document.createElement('div');
    selectedOptionDisplay.className = 'selected-option-display';

    // Append dropdownName and selectedOptionDisplay to the anchor
    anchor.appendChild(dropdownName);
    anchor.appendChild(selectedOptionDisplay);

    // Create the unordered list element
    const ul = document.createElement('ul');
    ul.className = 'dropdown-menu';
    ul.setAttribute('aria-labelledby', anchor_id);

    if(!allow_multiple) {
        // Conditionally add the "All" option
        if (need_all) {
            const allOption = document.createElement('li');
            const allLink = document.createElement('a');
            allLink.className = 'dropdown-item';
            allLink.href = 'javascript:;';
            allLink.textContent = 'All';
            allLink.addEventListener('click', () => {
                selectDropdown(dropdown, "All", allow_multiple);
            });
            allOption.appendChild(allLink);
            ul.appendChild(allOption);
        }

        // Conditionally add the "None" option
        if (need_none) {
            const noneOption = document.createElement('li');
            const noneLink = document.createElement('a');
            noneLink.className = 'dropdown-item';
            noneLink.href = 'javascript:;';
            noneLink.textContent = 'None';
            noneLink.addEventListener('click', () => {
                selectDropdown(dropdown, "", allow_multiple);
            });
            noneOption.appendChild(noneLink);
            ul.appendChild(noneOption);
        }
    }

    try {
        const response = await fetch(`/api/lookup/${category}/${type}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // Populate the list with new items
        data.forEach(item => {
            const li = document.createElement('li');
            li.classList.add("text-md");

            const flexContainer = document.createElement('div');
            flexContainer.style.display = 'flex';
            flexContainer.style.alignItems = 'center';

            const a = document.createElement('a');
            a.className = 'dropdown-item';
            a.classList.add('ms-auto'); // Align right
            a.href = 'javascript:;';
            a.textContent = item.value;

            if (allow_multiple) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'me-2';
                checkbox.addEventListener('change', () => {
                    selectDropdown(dropdown, null, allow_multiple);
                });
                flexContainer.appendChild(checkbox);
            } else {
                a.addEventListener('click', () => {
                    selectDropdown(dropdown, item.value, allow_multiple);
                });
            }

            flexContainer.appendChild(a);
            li.appendChild(flexContainer);
            ul.appendChild(li);
        });
        // Append the anchor and list to the dropdown div
        dropdown.appendChild(anchor);
    } catch (error) {
        console.error('Failed to fetch data:', error);
    }

    dropdown.appendChild(ul);

    // Initialize dropdown.selectedValue based on allow_multiple
    if(allow_multiple){
        (value || default_value).split(',').forEach(item => selectDropdown(dropdown, item, allow_multiple));
    }else{
        selectDropdown(dropdown, value || default_value, allow_multiple);
    }
}

async function selectDropdown(dropdown, value, allow_multiple) {
    const items = dropdown.querySelectorAll('li');
    items.forEach(item => {
        const a = item.querySelector('a');
        const checkMark = item.querySelector('span');
        const checkbox = item.querySelector('input[type="checkbox"]');

        // Clear previous highlights and checkmarks
        item.style.backgroundColor = '';
        if (checkMark) {
            checkMark.remove();
        }

        // console.log('textContent=>'+a.textContent.trim()+" value=>"+ value);
        if (a.textContent.trim() === value) {
            item.style.backgroundColor = '#f0f0f0'; // Highlight color
            if (allow_multiple) {
                checkbox.checked = true;
            }else {
                const newCheckMark = document.createElement('span');
                newCheckMark.textContent = ' ✓';
                newCheckMark.classList.add('ms-auto'); // Align right
                a.appendChild(newCheckMark);
            }
        }
    });

    // Store the selected value in the dropdown element
    if (allow_multiple) {
        const selectedValues = Array.from(items)
            .filter(item => item.querySelector('input[type="checkbox"]').checked)
            .map(item => item.querySelector('a').textContent.trim());
        dropdown.selectedValue = selectedValues.join(', ');
    } else {
        dropdown.selectedValue = value;
    }

    const dropdownName = dropdown.querySelector('.dropdown-name');
    const selectedOptionDisplay = dropdown.querySelector('.selected-option-display');
    selectedOptionDisplay.textContent = dropdown.selectedValue;
    selectedOptionDisplay.classList.add('text-truncate'); // Add class for text truncation


    if (dropdown.selectedValue === '' || dropdown.selectedValue == null) {
        selectedOptionDisplay.style.display = 'none';
        dropdownName.classList.remove("text-lg");
        dropdownName.classList.remove("text-xxs");
        dropdownName.classList.add("text-lg");
    } else {
        selectedOptionDisplay.style.display = 'block';
        dropdownName.classList.remove("text-lg");
        dropdownName.classList.remove("text-xxs");
        dropdownName.classList.add("text-xxs");
    }
    // console.log("=============>"+dropdown.selectedValue)
}
