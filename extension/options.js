/**
 * The one place broad host access can actually be asked for.
 *
 * `chrome.permissions.request()` requires an unspent user gesture. The service
 * worker's context-menu handler has to await the image fetch before it could
 * know whether a permission is even needed, and that await spends the gesture —
 * the call then throws "must be called during a user gesture" every time.
 *
 * A button the user clicks has a gesture that has not been spent on anything,
 * so the request works here and nowhere else.
 */
const ALL_SITES = { origins: ['*://*/*'] };

const button = document.getElementById('grant');
const status = document.getElementById('status');

function render(granted) {
  button.disabled = granted;
  button.textContent = granted ? 'Access granted' : 'Allow on all sites';
  status.textContent = granted
    ? 'ClearBG can read images on any site you right-click.'
    : '';
  status.className = granted ? 'status ok' : 'status';
}

chrome.permissions.contains(ALL_SITES).then(render);

button.addEventListener('click', async () => {
  try {
    render(await chrome.permissions.request(ALL_SITES));
  } catch (err) {
    status.textContent = String(err.message || err);
    status.className = 'status';
  }
});
