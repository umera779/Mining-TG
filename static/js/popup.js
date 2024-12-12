const popup = document.getElementById('popup');
        const overlay = document.getElementById('overlay');
        const closeBtn = document.getElementById('close-btn');
        const popupContent = document.getElementById('popup-content');
        const links = document.querySelectorAll('.ajax-link');

        // Function to show the pop-up
        function showPopup() {
            popup.classList.add('active');
            overlay.classList.add('active');
        }

        // Function to close the pop-up
        function closePopup() {
            popup.classList.remove('active');
            overlay.classList.remove('active');
            popupContent.innerHTML = ''; // Clear content when closing
        }

        // Attach event listener to all links
        links.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault(); // Prevent default link behavior

                const url = this.getAttribute('href'); // Get the URL from href

                // Fetch the content of the page
                fetch(url)
                    .then(response => {
                        if (response.ok) {
                            return response.text(); // Get response as text
                        }
                        throw new Error('Failed to fetch content');
                    })
                    .then(content => {
                        popupContent.innerHTML = content; // Load content into pop-up
                        showPopup(); // Show the pop-up
                    })
                    .catch(error => {
                        popupContent.innerHTML = `<p>Error loading content: ${error.message}</p>`;
                        showPopup(); // Show pop-up with error message
                    });
            });
        });

        // Close the pop-up when the close button is clicked
        closeBtn.addEventListener('click', closePopup);