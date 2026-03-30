---
name: frontend-api-integration
description: Expert knowledge of frontend JavaScript for API integration including fetch/axios patterns, async/await error handling, form validation and submission, pagination implementation, loading states, DOM manipulation, event listeners, query parameter building, and vanilla JS best practices. Use when working with public/script.js, adding UI features, debugging client-side API issues, implementing forms, or managing client-side state.
---

# Frontend API Integration Expert

This skill provides comprehensive expert knowledge of vanilla JavaScript for frontend API integration, with emphasis on modern async patterns, form handling, DOM manipulation, and user experience best practices.

## Fetch API Patterns

### Basic Fetch

```javascript
// GET request
async function getData() {
  try {
    const response = await fetch('/api/data');

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

// POST request
async function postData(data) {
  try {
    const response = await fetch('/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error posting data:', error);
    throw error;
  }
}
```

### Fetch with Authentication

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('authToken');

  const config = {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  };

  const response = await fetch(url, config);

  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
```

### Fetch with Timeout

```javascript
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
  const controller = new AbortController();
  const signal = controller.signal;

  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timeout');
    }

    throw error;
  }
}
```

## Async/Await Error Handling

### Try-Catch Pattern

```javascript
async function handleAPICall() {
  const loader = document.getElementById('loader');
  const errorMessage = document.getElementById('error');

  try {
    // Show loader
    loader.style.display = 'block';
    errorMessage.style.display = 'none';

    const data = await fetch('/api/data').then(r => r.json());

    // Process data
    displayData(data);

  } catch (error) {
    // Show error to user
    errorMessage.textContent = `Error: ${error.message}`;
    errorMessage.style.display = 'block';

    console.error('API call failed:', error);
  } finally {
    // Always hide loader
    loader.style.display = 'none';
  }
}
```

### Retry Logic

```javascript
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      const isLastAttempt = i === maxRetries - 1;

      if (isLastAttempt) {
        throw error;
      }

      // Wait before retrying (exponential backoff)
      const delay = Math.pow(2, i) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));

      console.log(`Retry attempt ${i + 1}/${maxRetries}`);
    }
  }
}
```

## Form Handling

### Form Validation and Submission

```javascript
// Cache form elements
const form = document.getElementById('searchForm');
const submitButton = document.getElementById('submitButton');

// Form submission handler
form.addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent default form submission

  // Validate form
  if (!validateForm()) {
    return;
  }

  // Disable submit button to prevent double submission
  submitButton.disabled = true;
  submitButton.textContent = 'Submitting...';

  try {
    const formData = getFormData();
    const result = await submitFormData(formData);

    // Handle success
    displaySuccessMessage('Form submitted successfully!');
    form.reset();

  } catch (error) {
    // Handle error
    displayErrorMessage(`Submission failed: ${error.message}`);
  } finally {
    // Re-enable submit button
    submitButton.disabled = false;
    submitButton.textContent = 'Submit';
  }
});

// Extract form data
function getFormData() {
  const formData = new FormData(form);
  const data = {};

  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }

  return data;
}

// Alternative: Using individual field values
function getFormDataManual() {
  return {
    keyword: document.getElementById('keyword').value.trim(),
    startDate: document.getElementById('startDate').value,
    endDate: document.getElementById('endDate').value,
    category: document.getElementById('category').value
  };
}
```

### Client-Side Validation

```javascript
function validateForm() {
  const errors = [];

  // Email validation
  const email = document.getElementById('email').value;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email) {
    errors.push('Email is required');
  } else if (!emailRegex.test(email)) {
    errors.push('Invalid email format');
  }

  // Date validation
  const startDate = new Date(document.getElementById('startDate').value);
  const endDate = new Date(document.getElementById('endDate').value);

  if (endDate < startDate) {
    errors.push('End date must be after start date');
  }

  // Required field validation
  const requiredFields = ['keyword', 'category'];

  for (const fieldId of requiredFields) {
    const field = document.getElementById(fieldId);
    if (!field.value.trim()) {
      errors.push(`${fieldId} is required`);
    }
  }

  // Display errors
  if (errors.length > 0) {
    displayValidationErrors(errors);
    return false;
  }

  clearValidationErrors();
  return true;
}

function displayValidationErrors(errors) {
  const errorContainer = document.getElementById('validationErrors');
  errorContainer.innerHTML = errors.map(err =>
    `<div class="error">${err}</div>`
  ).join('');
  errorContainer.style.display = 'block';
}

function clearValidationErrors() {
  const errorContainer = document.getElementById('validationErrors');
  errorContainer.innerHTML = '';
  errorContainer.style.display = 'none';
}
```

### Real-time Validation

```javascript
// Validate on blur (when user leaves field)
const emailInput = document.getElementById('email');

emailInput.addEventListener('blur', () => {
  const email = emailInput.value;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (email && !emailRegex.test(email)) {
    showFieldError(emailInput, 'Invalid email format');
  } else {
    clearFieldError(emailInput);
  }
});

function showFieldError(field, message) {
  field.classList.add('error');

  let errorDiv = field.nextElementSibling;
  if (!errorDiv || !errorDiv.classList.contains('field-error')) {
    errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
  }

  errorDiv.textContent = message;
}

function clearFieldError(field) {
  field.classList.remove('error');

  const errorDiv = field.nextElementSibling;
  if (errorDiv && errorDiv.classList.contains('field-error')) {
    errorDiv.remove();
  }
}
```

## Pagination Implementation

### Basic Pagination

```javascript
let currentPage = 1;
const recordsPerPage = 10;
let totalRecords = 0;

// Update pagination UI
function updatePagination(total) {
  totalRecords = total;
  const totalPages = Math.ceil(totalRecords / recordsPerPage);

  // Update record info
  const start = (currentPage - 1) * recordsPerPage + 1;
  const end = Math.min(currentPage * recordsPerPage, totalRecords);

  document.getElementById('recordInfo').textContent =
    `Showing ${start} to ${end} of ${totalRecords} records`;

  // Update buttons
  const prevButton = document.getElementById('prevButton');
  const nextButton = document.getElementById('nextButton');

  prevButton.disabled = currentPage === 1;
  nextButton.disabled = currentPage >= totalPages;
}

// Pagination event handlers
document.getElementById('prevButton').addEventListener('click', async () => {
  if (currentPage > 1) {
    currentPage -= 1;
    await fetchResults();
  }
});

document.getElementById('nextButton').addEventListener('click', async () => {
  const totalPages = Math.ceil(totalRecords / recordsPerPage);

  if (currentPage < totalPages) {
    currentPage += 1;
    await fetchResults();
  }
});

// Fetch paginated results
async function fetchResults() {
  const offset = (currentPage - 1) * recordsPerPage;

  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      limit: recordsPerPage,
      offset: offset,
      ...getFilters()
    })
  });

  const data = await response.json();

  displayResults(data.results);
  updatePagination(data.total);
}
```

### Page Number Pagination

```javascript
function renderPageNumbers(currentPage, totalPages) {
  const pageNumbersContainer = document.getElementById('pageNumbers');
  pageNumbersContainer.innerHTML = '';

  // Show first page
  addPageButton(1, currentPage, pageNumbersContainer);

  // Show ellipsis if needed
  if (currentPage > 3) {
    pageNumbersContainer.innerHTML += '<span>...</span>';
  }

  // Show pages around current page
  for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
    addPageButton(i, currentPage, pageNumbersContainer);
  }

  // Show ellipsis if needed
  if (currentPage < totalPages - 2) {
    pageNumbersContainer.innerHTML += '<span>...</span>';
  }

  // Show last page
  if (totalPages > 1) {
    addPageButton(totalPages, currentPage, pageNumbersContainer);
  }
}

function addPageButton(pageNum, currentPage, container) {
  const button = document.createElement('button');
  button.textContent = pageNum;
  button.className = pageNum === currentPage ? 'active' : '';
  button.addEventListener('click', () => goToPage(pageNum));
  container.appendChild(button);
}

async function goToPage(pageNum) {
  currentPage = pageNum;
  await fetchResults();
}
```

## Loading States and User Feedback

### Loading Spinner

```javascript
const loader = document.querySelector('.loader');

function showLoader() {
  loader.style.display = 'block';
}

function hideLoader() {
  loader.style.display = 'none';
}

// Usage
async function loadData() {
  showLoader();

  try {
    const data = await fetch('/api/data').then(r => r.json());
    displayData(data);
  } catch (error) {
    showError(error.message);
  } finally {
    hideLoader();
  }
}
```

### Skeleton Screens

```javascript
function showSkeleton() {
  const container = document.getElementById('resultsContainer');
  container.innerHTML = `
    <div class="skeleton-item">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-line"></div>
    </div>
    <div class="skeleton-item">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-line"></div>
    </div>
  `;
}

// CSS for skeleton
/*
.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin: 8px 0;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
*/
```

### Progress Indicators

```javascript
function updateProgress(current, total) {
  const percentage = (current / total) * 100;

  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');

  progressBar.style.width = `${percentage}%`;
  progressText.textContent = `${current} of ${total} items processed`;
}

// Usage for batch operations
async function processBatchItems(items) {
  for (let i = 0; i < items.length; i++) {
    await processItem(items[i]);
    updateProgress(i + 1, items.length);
  }
}
```

## DOM Manipulation

### Creating and Appending Elements

```javascript
function createResultCard(data) {
  // Create elements
  const card = document.createElement('div');
  card.className = 'result-card';

  const title = document.createElement('h3');
  title.textContent = data.title;

  const description = document.createElement('p');
  description.textContent = data.description;

  const link = document.createElement('a');
  link.href = data.url;
  link.textContent = 'View Details';
  link.target = '_blank';

  // Append elements
  card.appendChild(title);
  card.appendChild(description);
  card.appendChild(link);

  return card;
}

function displayResults(results) {
  const container = document.getElementById('resultsContainer');

  // Clear existing content
  container.innerHTML = '';

  if (results.length === 0) {
    container.innerHTML = '<p class="no-results">No results found</p>';
    return;
  }

  // Add each result
  results.forEach(result => {
    const card = createResultCard(result);
    container.appendChild(card);
  });
}
```

### Template Literals for HTML

```javascript
function displayResults(results) {
  const container = document.getElementById('resultsContainer');

  if (results.length === 0) {
    container.innerHTML = '<p class="no-results">No results found</p>';
    return;
  }

  const html = results.map(result => `
    <div class="result-card">
      <h3>${escapeHtml(result.title)}</h3>
      <p>${escapeHtml(result.description)}</p>
      <a href="${escapeHtml(result.url)}" target="_blank">View Details</a>
    </div>
  `).join('');

  container.innerHTML = html;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

### Table Rendering

```javascript
function renderTable(data) {
  const tableBody = document.getElementById('resultsTable').querySelector('tbody');

  // Clear existing rows
  tableBody.innerHTML = '';

  if (data.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="4">No results found</td></tr>';
    return;
  }

  // Add rows
  data.forEach(item => {
    const row = document.createElement('tr');

    row.innerHTML = `
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.email)}</td>
      <td>${formatDate(item.createdAt)}</td>
      <td>
        <button onclick="viewDetails('${item.id}')">View</button>
        <button onclick="deleteItem('${item.id}')">Delete</button>
      </td>
    `;

    tableBody.appendChild(row);
  });
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
```

## Event Listeners

### Event Delegation

```javascript
// Instead of adding listeners to each button
// Add one listener to parent container

const resultsContainer = document.getElementById('resultsContainer');

resultsContainer.addEventListener('click', (event) => {
  // Check if clicked element is a delete button
  if (event.target.classList.contains('delete-btn')) {
    const itemId = event.target.dataset.id;
    deleteItem(itemId);
  }

  // Check if clicked element is a view button
  if (event.target.classList.contains('view-btn')) {
    const itemId = event.target.dataset.id;
    viewItem(itemId);
  }
});
```

### Debouncing User Input

```javascript
function debounce(func, delay) {
  let timeoutId;

  return function(...args) {
    clearTimeout(timeoutId);

    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

// Search as user types (debounced)
const searchInput = document.getElementById('searchInput');

const debouncedSearch = debounce(async (query) => {
  if (query.length < 3) return;

  const results = await searchAPI(query);
  displaySuggestions(results);
}, 300); // Wait 300ms after user stops typing

searchInput.addEventListener('input', (event) => {
  debouncedSearch(event.target.value);
});
```

### Throttling Events

```javascript
function throttle(func, limit) {
  let inThrottle;

  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;

      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Throttle scroll events
const throttledScroll = throttle(() => {
  console.log('Scroll event handled');
  // Handle scroll
}, 100);

window.addEventListener('scroll', throttledScroll);
```

## Query Parameter Building

### Building URL Query Strings

```javascript
function buildQueryString(params) {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    // Skip empty values
    if (value === '' || value === null || value === undefined) {
      continue;
    }

    // Handle arrays
    if (Array.isArray(value)) {
      value.forEach(item => query.append(key, item));
    } else {
      query.append(key, value);
    }
  }

  return query.toString();
}

// Usage
const params = {
  keyword: 'test',
  page: 1,
  categories: ['tech', 'news'],
  sort: 'date'
};

const queryString = buildQueryString(params);
// Result: keyword=test&page=1&categories=tech&categories=news&sort=date

const url = `/api/search?${queryString}`;
```

### Building Filter Objects

```javascript
function buildFilters() {
  const filters = {};

  // Get keyword
  const keyword = document.getElementById('keyword').value.trim();
  if (keyword) {
    filters.keywords = [keyword];
  }

  // Get date range
  const startDate = document.getElementById('startDate').value;
  const endDate = document.getElementById('endDate').value;

  if (startDate && endDate) {
    filters.time_period = [{
      start_date: startDate,
      end_date: endDate,
      date_type: document.getElementById('dateType').value
    }];
  }

  // Get award types
  const awardType = document.getElementById('awardType').value;

  if (awardType === 'all_contracts') {
    filters.award_type_codes = ['A', 'B', 'C', 'D'];
  } else if (awardType === 'all_grants') {
    filters.award_type_codes = ['02', '03', '04', '05'];
  } else if (awardType) {
    filters.award_type_codes = [awardType];
  }

  // Get agency filter (if both type and details provided)
  const agencyType = document.getElementById('agencyType').value;
  const agencyDetails = document.getElementById('agencyDetails').value;

  if (agencyType && agencyDetails) {
    filters.agencies = [{
      type: agencyDetails, // 'awarding' or 'funding'
      tier: 'toptier',
      name: agencyType
    }];
  }

  return filters;
}
```

## Dynamic URL Generation

```javascript
function generateRecipientURL(recipient, filters) {
  const baseURL = 'https://www.usaspending.gov/recipient';
  const recipientId = recipient.id;

  // Build query parameters from filters
  const params = new URLSearchParams();

  if (filters.time_period && filters.time_period[0]) {
    params.append('fy', getFiscalYear(filters.time_period[0].end_date));
  }

  if (filters.award_type_codes) {
    params.append('award_type', filters.award_type_codes.join(','));
  }

  return `${baseURL}/${recipientId}?${params.toString()}`;
}

function getFiscalYear(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth();

  // Federal fiscal year starts in October
  return month >= 9 ? year + 1 : year;
}
```

## Error Handling and User Messages

### Toast Notifications

```javascript
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  // Show toast
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);

  // Hide and remove after 3 seconds
  setTimeout(() => {
    toast.classList.remove('show');

    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// Usage
showToast('Data saved successfully!', 'success');
showToast('An error occurred', 'error');
showToast('Loading...', 'info');
```

### Modal Dialogs

```javascript
function showModal(title, message, onConfirm) {
  const modal = document.getElementById('modal');
  const modalTitle = document.getElementById('modalTitle');
  const modalMessage = document.getElementById('modalMessage');
  const confirmButton = document.getElementById('modalConfirm');
  const cancelButton = document.getElementById('modalCancel');

  modalTitle.textContent = title;
  modalMessage.textContent = message;

  modal.style.display = 'block';

  // Remove old event listeners
  const newConfirmButton = confirmButton.cloneNode(true);
  confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);

  // Add new event listener
  newConfirmButton.addEventListener('click', () => {
    modal.style.display = 'none';
    if (onConfirm) onConfirm();
  });

  cancelButton.addEventListener('click', () => {
    modal.style.display = 'none';
  });
}

// Usage
showModal(
  'Delete Item',
  'Are you sure you want to delete this item?',
  () => {
    deleteItem(itemId);
  }
);
```

## Local Storage

### Saving and Loading State

```javascript
// Save search filters to local storage
function saveFilters(filters) {
  localStorage.setItem('searchFilters', JSON.stringify(filters));
}

// Load filters from local storage
function loadFilters() {
  const saved = localStorage.getItem('searchFilters');

  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (error) {
      console.error('Error parsing saved filters:', error);
      return null;
    }
  }

  return null;
}

// Apply saved filters to form
function applySavedFilters() {
  const filters = loadFilters();

  if (!filters) return;

  if (filters.keyword) {
    document.getElementById('keyword').value = filters.keyword;
  }

  if (filters.startDate) {
    document.getElementById('startDate').value = filters.startDate;
  }

  if (filters.endDate) {
    document.getElementById('endDate').value = filters.endDate;
  }
}

// Load saved filters when page loads
document.addEventListener('DOMContentLoaded', () => {
  applySavedFilters();
});
```

### Session Storage

```javascript
// Use sessionStorage for temporary data (cleared when tab closes)
function saveCurrentPage(page) {
  sessionStorage.setItem('currentPage', page);
}

function getCurrentPage() {
  return parseInt(sessionStorage.getItem('currentPage')) || 1;
}
```

## Best Practices

### 1. Cache DOM Elements

```javascript
// GOOD - Cache DOM references
const form = document.getElementById('searchForm');
const resultsContainer = document.getElementById('resultsContainer');
const loader = document.querySelector('.loader');
const errorMessage = document.getElementById('errorMessage');

function updateUI() {
  resultsContainer.innerHTML = '...';
  loader.style.display = 'none';
}

// BAD - Repeated DOM queries
function updateUI() {
  document.getElementById('resultsContainer').innerHTML = '...';
  document.querySelector('.loader').style.display = 'none';
}
```

### 2. Use Event Delegation

```javascript
// GOOD - One listener on parent
document.getElementById('resultsContainer').addEventListener('click', (e) => {
  if (e.target.classList.contains('delete-btn')) {
    handleDelete(e.target.dataset.id);
  }
});

// BAD - Listener on each button
document.querySelectorAll('.delete-btn').forEach(btn => {
  btn.addEventListener('click', () => handleDelete(btn.dataset.id));
});
```

### 3. Avoid Memory Leaks

```javascript
// Clean up event listeners when removing elements
function removeElement(element) {
  // Clone node to remove all event listeners
  const clone = element.cloneNode(true);
  element.parentNode.replaceChild(clone, element);
}

// Remove listeners when navigating away
window.addEventListener('beforeunload', () => {
  // Clean up listeners, timers, etc.
  clearInterval(pollingInterval);
});
```

### 4. Progressive Enhancement

```javascript
// Check for feature support before using
if ('IntersectionObserver' in window) {
  // Use Intersection Observer for lazy loading
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        loadImage(entry.target);
      }
    });
  });
} else {
  // Fallback: load all images immediately
  loadAllImages();
}
```

### 5. Error Boundaries

```javascript
// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);

  showToast('An unexpected error occurred. Please refresh the page.', 'error');

  // Log to error tracking service
  logError(event.error);
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);

  showToast('An error occurred. Please try again.', 'error');

  // Log to error tracking service
  logError(event.reason);
});
```

## Complete Example: Search Form with API Integration

```javascript
// Cache DOM elements
const searchForm = document.getElementById('searchForm');
const resultsTable = document.getElementById('resultsTable').querySelector('tbody');
const resultsContainer = document.getElementById('resultsContainer');
const loader = document.querySelector('.loader');
const errorMessage = document.getElementById('errorMessage');
const prevButton = document.getElementById('prevButton');
const nextButton = document.getElementById('nextButton');
const recordInfo = document.getElementById('recordInfo');

// State
let currentPage = 1;
const recordsPerPage = 10;
let totalRecords = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  applySavedFilters();
});

function setupEventListeners() {
  searchForm.addEventListener('submit', handleSearch);
  prevButton.addEventListener('click', handlePrevPage);
  nextButton.addEventListener('click', handleNextPage);
}

async function handleSearch(event) {
  event.preventDefault();
  currentPage = 1;
  await fetchResults();
}

async function handlePrevPage() {
  if (currentPage > 1) {
    currentPage -= 1;
    await fetchResults();
  }
}

async function handleNextPage() {
  const totalPages = Math.ceil(totalRecords / recordsPerPage);

  if (currentPage < totalPages) {
    currentPage += 1;
    await fetchResults();
  }
}

async function fetchResults() {
  // Show loader, hide errors
  loader.style.display = 'block';
  errorMessage.style.display = 'none';
  resultsContainer.style.display = 'none';

  try {
    // Build filters from form
    const filters = buildFilters();

    // Save filters to local storage
    saveFilters(filters);

    // Fetch total count
    const countData = await fetchTotalCount(filters);
    totalRecords = countData.count;

    // Fetch paginated results
    const resultsData = await fetchPaginatedResults(filters);

    // Display results
    renderResults(resultsData.results);
    updatePagination();

    resultsContainer.style.display = 'block';

  } catch (error) {
    console.error('Error fetching results:', error);

    errorMessage.textContent = `Error: ${error.message}`;
    errorMessage.style.display = 'block';
  } finally {
    loader.style.display = 'none';
  }
}

async function fetchTotalCount(filters) {
  const response = await fetch('/api/count', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filters })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

async function fetchPaginatedResults(filters) {
  const offset = (currentPage - 1) * recordsPerPage;

  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filters,
      limit: recordsPerPage,
      page: currentPage,
      offset
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

function renderResults(results) {
  resultsTable.innerHTML = '';

  if (results.length === 0) {
    resultsTable.innerHTML = '<tr><td colspan="4">No results found</td></tr>';
    return;
  }

  results.forEach(result => {
    const row = document.createElement('tr');

    row.innerHTML = `
      <td>${escapeHtml(result.recipient_name)}</td>
      <td>${escapeHtml(result.award_id)}</td>
      <td>${formatCurrency(result.award_amount)}</td>
      <td>
        <a href="${generateRecipientURL(result)}" target="_blank">View Details</a>
      </td>
    `;

    resultsTable.appendChild(row);
  });
}

function updatePagination() {
  const totalPages = Math.ceil(totalRecords / recordsPerPage);
  const start = (currentPage - 1) * recordsPerPage + 1;
  const end = Math.min(currentPage * recordsPerPage, totalRecords);

  recordInfo.textContent = `Showing ${start} to ${end} of ${totalRecords} records`;

  prevButton.disabled = currentPage === 1;
  nextButton.disabled = currentPage >= totalPages;
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

## Performance Optimization

### Lazy Loading Images

```javascript
const images = document.querySelectorAll('img[data-src]');

const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
      observer.unobserve(img);
    }
  });
});

images.forEach(img => imageObserver.observe(img));
```

### Virtual Scrolling for Large Lists

```javascript
// Only render visible items
function renderVirtualList(items, containerHeight, itemHeight) {
  const container = document.getElementById('listContainer');
  const scrollTop = container.scrollTop;

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.ceil((scrollTop + containerHeight) / itemHeight);

  const visibleItems = items.slice(startIndex, endIndex);

  container.innerHTML = '';
  container.style.height = `${items.length * itemHeight}px`;

  visibleItems.forEach((item, index) => {
    const element = createListItem(item);
    element.style.position = 'absolute';
    element.style.top = `${(startIndex + index) * itemHeight}px`;
    container.appendChild(element);
  });
}
```

## Resources

- MDN Web Docs - Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- MDN - Working with Forms: https://developer.mozilla.org/en-US/docs/Learn/Forms
- JavaScript.info: https://javascript.info/
- Web.dev - Fast Load Times: https://web.dev/fast/
- Google Developers - UX Patterns: https://developers.google.com/web/fundamentals/design-and-ux/ux-basics
