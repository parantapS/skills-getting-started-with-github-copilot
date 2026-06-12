document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      // Reset the select so repeated fetches don't duplicate options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants section (bulleted list)
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";
        participantsSection.innerHTML = `<h5>Participants</h5>`;

        const ul = document.createElement("ul");
        ul.className = "participants-list";

        if (details.participants && details.participants.length > 0) {
          details.participants.forEach((p) => {
            const li = document.createElement("li");
            li.className = "participant-item";
            li.dataset.activity = name;
            li.dataset.email = p;

            const span = document.createElement("span");
            span.className = "participant-email";
            span.textContent = p;

            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "participant-delete";
            deleteBtn.title = "Unregister participant";
            deleteBtn.dataset.activity = name;
            deleteBtn.dataset.email = p;
            deleteBtn.textContent = "×";

            li.appendChild(span);
            li.appendChild(deleteBtn);
            ul.appendChild(li);
          });
        } else {
          const li = document.createElement("li");
          li.className = "participant-item empty";
          li.textContent = "No participants yet";
          ul.appendChild(li);
        }

        participantsSection.appendChild(ul);
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    if (!activity) {
      messageDiv.textContent = "Please select an activity.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      setTimeout(() => messageDiv.classList.add("hidden"), 3000);
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh the activities list to show new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Event delegation for delete buttons on participant items
  activitiesList.addEventListener("click", async (event) => {
    const target = event.target;
    if (target.classList.contains("participant-delete")) {
      const activityName = target.dataset.activity;
      const email = target.dataset.email;

      if (!activityName || !email) return;

      // Optional: simple confirmation
      const ok = confirm(`Unregister ${email} from ${activityName}?`);
      if (!ok) return;

      try {
        const resp = await fetch(
          `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
          { method: "DELETE" }
        );

        const data = await resp.json();
        if (resp.ok) {
          messageDiv.textContent = data.message;
          messageDiv.className = "success";
          messageDiv.classList.remove("hidden");
          // Refresh list
          fetchActivities();
        } else {
          messageDiv.textContent = data.detail || "Failed to unregister";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
        }

        setTimeout(() => messageDiv.classList.add("hidden"), 4000);
      } catch (err) {
        console.error("Error unregistering:", err);
        messageDiv.textContent = "Failed to unregister. Try again.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        setTimeout(() => messageDiv.classList.add("hidden"), 4000);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
