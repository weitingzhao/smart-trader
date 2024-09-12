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
    const anchor_id = `navbar_${category}_${type}`;

    // Create the anchor element
    const anchor = document.createElement('a');
    anchor.href = 'javascript:;';
    anchor.className = 'form-control bg-gradient-light dropdown-toggle w-100';
    anchor.style.height = '50px';
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