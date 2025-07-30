// ====== Helper Functions ======

// Get cookie value by name
function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) {
      return decodeURIComponent(value);
    }
  }
  return null;
}

// ====== Task 1: Login ======
// Handle login form submission, call API, save token cookie, redirect
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = loginForm.querySelector('input[name="email"]').value.trim();
      const password = loginForm.querySelector('input[name="password"]').value.trim();

      if (!email || !password) {
        alert('Please fill in both email and password.');
        return;
      }

      try {
        const response = await fetch('http://0.0.0.0:5000/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
        });

        if (response.ok) {
          const data = await response.json();
          // Save JWT token in cookie (valid for 1 day)
          document.cookie = `token=${data.access_token}; path=/; max-age=86400`;
          window.location.href = 'index.html'; // Redirect to main page
        } else {
          const errData = await response.json();
          alert('Login failed: ' + (errData.message || response.statusText));
        }
      } catch (error) {
        alert('Network error: ' + error.message);
      }
    });
  }
});

// ====== Task 2: Index page ======
// Show/hide login link based on auth, fetch and display places, client-side price filter
document.addEventListener('DOMContentLoaded', () => {
  const loginLink = document.getElementById('login-link');
  const priceFilter = document.getElementById('price-filter');
  const placesList = document.getElementById('places-list');
  let allPlaces = []; // to store fetched places for filtering

  // Check user auth and toggle login link visibility
  function checkAuthentication() {
    const token = getCookie('token');
    if (!token) {
      if (loginLink) loginLink.style.display = 'block';
    } else {
      if (loginLink) loginLink.style.display = 'none';
      fetchPlaces(token);
    }
  }

  // Fetch places data from API
  async function fetchPlaces(token) {
    try {
      const response = await fetch('http://0.0.0.0:5000/api/v1/places', {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });
      if (response.ok) {
        const data = await response.json();
        allPlaces = data; // save for filtering
        displayPlaces(allPlaces);
      } else {
        alert('Failed to load places');
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    }
  }

  // Display places in the DOM
  function displayPlaces(places) {
    if (!placesList) return;
    placesList.innerHTML = ''; // clear existing

    places.forEach(place => {
      const placeDiv = document.createElement('div');
      placeDiv.classList.add('place-item');
      placeDiv.dataset.price = place.price_by_night;

      placeDiv.innerHTML = `
        <h3>${place.name}</h3>
        <p>${place.description}</p>
        <p><strong>Location:</strong> ${place.city}, ${place.state}</p>
        <p><strong>Price:</strong> $${place.price_by_night} per night</p>
        <a href="place.html?place_id=${place.id}">View Details</a>
      `;
      placesList.appendChild(placeDiv);
    });
  }

  // Filter places by price dropdown
  if (priceFilter) {
    priceFilter.addEventListener('change', (event) => {
      const maxPrice = event.target.value;
      let filtered = allPlaces;

      if (maxPrice !== 'All') {
        const max = parseInt(maxPrice);
        filtered = allPlaces.filter(place => place.price_by_night <= max);
      }
      displayPlaces(filtered);
    });
  }

  checkAuthentication();
});

// ====== Task 3: Place details page ======
// Fetch place details, show add review form if authenticated
document.addEventListener('DOMContentLoaded', () => {
  const placeDetailsSection = document.getElementById('place-details');
  const addReviewSection = document.getElementById('add-review');

  const token = getCookie('token');
  const placeId = getPlaceIdFromURL();

  if (!placeId) {
    alert('Place ID not found in URL');
    return;
  }

  // Show or hide add review form based on auth
  if (addReviewSection) {
    if (!token) {
      addReviewSection.style.display = 'none';
    } else {
      addReviewSection.style.display = 'block';
    }
  }

  // Fetch place details from API
  async function fetchPlaceDetails(token, placeId) {
    try {
      const response = await fetch('http://0.0.0.0:5000/api/v1/places/' + placeId, {
        headers: token ? { 'Authorization': 'Bearer ' + token } : {}
      });
      if (response.ok) {
        const place = await response.json();
        displayPlaceDetails(place);
      } else {
        alert('Failed to fetch place details');
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    }
  }

  // Display detailed info about the place
  function displayPlaceDetails(place) {
    if (!placeDetailsSection) return;
    placeDetailsSection.innerHTML = '';

    // Amenities list
    const amenitiesHTML = place.amenities && place.amenities.length > 0
      ? '<ul>' + place.amenities.map(a => `<li>${a.name}</li>`).join('') + '</ul>'
      : '<p>No amenities listed.</p>';

    // Reviews list
    const reviewsHTML = place.reviews && place.reviews.length > 0
      ? '<ul>' + place.reviews.map(r => `<li>${r.user.name}: ${r.text}</li>`).join('') + '</ul>'
      : '<p>No reviews yet.</p>';

    placeDetailsSection.innerHTML = `
      <h2>${place.name}</h2>
      <p>${place.description}</p>
      <p><strong>Price:</strong> $${place.price_by_night} per night</p>
      <h3>Amenities</h3>
      ${amenitiesHTML}
      <h3>Reviews</h3>
      ${reviewsHTML}
    `;
  }

  fetchPlaceDetails(token, placeId);
});

// Helper function to get place_id from URL query params (used in task 3 and 4)
function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('place_id');
}

// ====== Task 4: Add Review ======
// Add review form submit with auth check, send POST request with JWT token
document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('token');
  if (!token) {
    // Redirect if not authenticated
    window.location.href = 'index.html';
    return;
  }

  const placeId = getPlaceIdFromURL();
  if (!placeId) {
    alert('Place ID not found.');
    return;
  }

  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = reviewForm.querySelector('textarea[name="review"]').value.trim();

      if (reviewText.length === 0) {
        alert('Please enter a review');
        return;
      }

      try {
        const response = await fetch('http://0.0.0.0:5000/api/v1/places/' + placeId + '/reviews', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
          },
          body: JSON.stringify({ text: reviewText })
        });

        if (response.ok) {
          alert('Review submitted successfully!');
          reviewForm.reset();
        } else {
          alert('Failed to submit review');
        }
      } catch (error) {
        alert('Error submitting review: ' + error.message);
      }
    });
  }
});