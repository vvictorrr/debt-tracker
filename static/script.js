document.addEventListener('DOMContentLoaded', () => {
    // your code here...
    const threshold = 5;
    const availableList = document.getElementById('available-friends');
    const selectedList = document.getElementById('selected-friends');
    const showMoreBtn = document.getElementById('show-more-btn');
    let expanded = false;

    function initCutoff() {
        const items = availableList.querySelectorAll('li');
        items.forEach((li, idx) => {
            if (idx >= threshold) li.classList.add('d-none');
        });
        
        // always check the current count and show/hide accordingly
        showMoreBtn.style.display = items.length > threshold ? 'block' : 'none';
        
        // reset the button text if hiding it
        if (items.length <= threshold) {
            expanded = false;
            showMoreBtn.textContent = 'Show More';
        }
    }

    // toggle between "Show More" and "Show Less"
    showMoreBtn.addEventListener('click', () => {
        const items = availableList.querySelectorAll('li');
        expanded = !expanded;
        items.forEach((li, idx) => {
            if (idx >= threshold) li.classList.toggle('d-none', !expanded);
        });
        showMoreBtn.textContent = expanded ? 'Show Less' : 'Show More';
    });

    // move friend from available to selected
    availableList.addEventListener('click', (e) => {
        const li = e.target.closest('li');
        if (!li) return;
        const id = li.dataset.id;
        const name = li.dataset.name;
        const username = li.dataset.username;

        li.remove();

        const div = document.createElement('li');
        div.classList.add('selected-item', 'border', 'rounded', 'p-2', 'mb-2', 'd-flex', 'align-items-center', 'justify-content-between');
        div.dataset.id = id;
        div.dataset.name = name;
        div.dataset.username = username;
        div.innerHTML = `
            <span class="me-2">${name} (${username})</span>
            <input type="number" name="debtor_${id}" class="form-control me-2" step="0.01" min="0" placeholder="0.00" required style="width: 100px;">
            <button type="button" class="btn btn-danger btn-sm remove-btn">&minus;</button>
        `;
        selectedList.appendChild(div);

        initCutoff();
    });

    // move friend back from selected to available
    selectedList.addEventListener('click', (e) => {
        if (!e.target.classList.contains('remove-btn')) return;
        const div = e.target.closest('.selected-item');
        const id = div.dataset.id;
        const name = div.dataset.name;
        const username = div.dataset.username;

        div.remove();

        const li = document.createElement('li');
        li.classList.add('border', 'rounded', 'p-2', 'mb-2', 'd-flex', 'justify-content-between', 'align-items-center');
        li.dataset.id = id;
        li.dataset.name = name;
        li.dataset.username = username;
        li.innerHTML = `<span>${name} (${username})</span>`;
        availableList.appendChild(li);

        initCutoff();
    });

    initCutoff();
    //Past payments
    let visibleCount = threshold;

    const rows = Array.from(document.querySelectorAll(".payment-row"));
    const showMoreBtn2 = document.getElementById("show-more-payments");
    const showLessBtn = document.getElementById("show-less-payments");

    function updateTableDisplay() {
        rows.forEach((row, index) => {
            row.style.display = index < visibleCount ? "" : "none";
        });

        if (showMoreBtn2) {
            showMoreBtn2.style.display = visibleCount < rows.length ? "inline-block" : "none";
        }
        if (showLessBtn) {
            showLessBtn.style.display = visibleCount > threshold ? "inline-block" : "none";
        }
    }

    if (showMoreBtn2 && showLessBtn && rows.length > 0) {
        showMoreBtn2.addEventListener("click", () => {
            visibleCount = Math.min(visibleCount + threshold, rows.length);
            updateTableDisplay();
        });

        showLessBtn.addEventListener("click", () => {
            visibleCount = Math.max(threshold, visibleCount - threshold);
            updateTableDisplay();
        });

        updateTableDisplay(); // initialize
    }
});