document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.element-table-delete-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            let userConfirmed = false;
            let sidConfirmed = false;

            // Check if the form contains a username input
            const usernameInput = form.querySelector('input[name="username"]');
            if (usernameInput) {
                const username = usernameInput.value;
                // Show confirmation dialog with the username
                userConfirmed = confirm(`Are you sure you want to delete the user: ${username}?`);
            }
            
            // Check if the form contains a session id (sid) input
            const sidInput = form.querySelector('input[name="sid"]');
            if (sidInput) {
                const sid = sidInput.value;
                // Show confirmation dialog with the session id
                sidConfirmed = confirm(`Are you sure you want to terminate the session: ${sid}?`);
            }

            // If user cancels either of the actions, prevent form submission
            if (!userConfirmed || !sidConfirmed) {
                event.preventDefault();
            }
        });
    });
});