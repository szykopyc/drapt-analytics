document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.element-table-delete-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            let shouldPrevent = false;

            // Check if the form contains a username input
            const usernameInput = form.querySelector('input[name="username"]');
            if (usernameInput) {
                const username = usernameInput.value;
                // Show confirmation dialog with the username
                const userConfirmed = confirm(`Are you sure you want to delete the user: ${username}?`);
                if (!userConfirmed) shouldPrevent = true; // Mark to prevent submission
            }
            
            // Check if the form contains a session id (sid) input
            const sidInput = form.querySelector('input[name="sid"]');
            if (sidInput) {
                const sid = sidInput.value;
                // Show confirmation dialog with the session id
                const sidConfirmed = confirm(`Are you sure you want to terminate the session: ${sid}?`);
                if (!sidConfirmed) shouldPrevent = true; // Mark to prevent submission
            }

            // Prevent form submission if any confirmation was canceled
            if (shouldPrevent) {
                event.preventDefault();
            }
        });
    });
});