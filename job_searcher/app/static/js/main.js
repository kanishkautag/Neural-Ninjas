// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Job search form submission
    const jobSearchForm = document.getElementById('job-search-form');
    if (jobSearchForm) {
        jobSearchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Searching...';
            submitButton.disabled = true;
            
            // Gather form data
            const formData = {
                industry: document.getElementById('industry').value,
                keywords: document.getElementById('keywords').value,
                location: document.getElementById('location').value,
                time_period: document.getElementById('time-period').value
            };
            
            try {
                // Send request to API
                const response = await fetch('/api/search-jobs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayJobResults(data.data);
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            } finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
    
    // Skillset form submission
    const skillsetForm = document.getElementById('skillset-form');
    if (skillsetForm) {
        skillsetForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Getting Skillset...';
            submitButton.disabled = true;
            
            // Gather form data
            const formData = {
                profession: document.getElementById('profession').value,
                experience_level: document.getElementById('experience-level').value
            };
            
            try {
                // Send request to API
                const response = await fetch('/api/get-skillset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displaySkillsetResults(data.data);
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            } finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});

// Function to display job search results
function displayJobResults(data) {
    // Hide skillset results and show job results
    document.getElementById('skillset-results').classList.add('hidden');
    document.getElementById('job-results').classList.remove('hidden');
    
    // Display market summary
    const marketSummaryElement = document.getElementById('market-summary');
    marketSummaryElement.textContent = data.market_summary;
    
    // Display job listings
    const jobsContainer = document.getElementById('jobs-container');
    jobsContainer.innerHTML = '';
    
    if (data.jobs.length === 0) {
        jobsContainer.innerHTML = '<p class="text-center text-gray-400">No job openings found matching your criteria.</p>';
        return;
    }
    
    data.jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'bg-gray-700 rounded-lg p-4 border border-gray-600';
        jobCard.innerHTML = `
            <h3 class="text-lg font-bold">${job.title}</h3>
            <p class="text-gray-400">${job.source}</p>
            <div class="text-sm text-gray-300 mt-2">${job.snippet}</div>
            <a href="${job.link}" target="_blank" class="text-blue-400 mt-2 block">View Job</a>
        `;
        jobsContainer.appendChild(jobCard);
    });
}

// Function to display skillset results
function displaySkillsetResults(data) {
    // Hide job results and show skillset results
    document.getElementById('job-results').classList.add('hidden');
    document.getElementById('skillset-results').classList.remove('hidden');
    
    // Display skillset details
    const skillsetDetails = document.getElementById('skillset-details');
    skillsetDetails.innerHTML = `
        <h3 class="text-xl font-bold mb-4">${data.profession} - ${data.experience_level}</h3>
    `;
    
    // Display each skillset section
    for (const [section, skills] of Object.entries(data.skillset)) {
        if (skills.length > 0) {
            const sectionElement = document.createElement('div');
            sectionElement.className = 'mb-6';
            sectionElement.innerHTML = `
                <h4 class="text-lg font-semibold mb-2">${section}</h4>
                <ul class="list-disc pl-6 text-gray-300">
                    ${skills.map(skill => `<li>${skill}</li>`).join('')}
                </ul>
            `;
            skillsetDetails.appendChild(sectionElement);
        }
    }
}