const API_URL = "http://localhost:8000";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}


// =========================================================
// LOAD REQUESTS
// =========================================================

async function loadPurchaseRequests() {

    const container =
        document.getElementById("requestsContainer");

    try {

        const response = await fetch(
            `${API_URL}/api/farmer/purchase-requests`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.status === 401) {
            localStorage.clear();
            window.location.href = "login.html";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to load requests"
            );
        }

        renderRequests(data.requests);

    } catch (error) {

        container.innerHTML = `
            <div class="empty">
                <h3>Unable to load requests</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}


// =========================================================
// RENDER REQUESTS
// =========================================================

function renderRequests(requests) {

    const container =
        document.getElementById("requestsContainer");

    if (!requests.length) {

        container.innerHTML = `
            <div class="empty">
                <h3>No Purchase Requests</h3>
                <p>
                    You don't have any incoming requests yet.
                </p>
            </div>
        `;

        return;
    }


    container.innerHTML = requests.map(request => {

        const statusClass =
            request.status === "PENDING"
                ? "status-pending"
                : request.status === "ACCEPTED"
                    ? "status-accepted"
                    : "status-rejected";


        let actions = "";

        if (request.status === "PENDING") {

            actions = `
                <div class="actions">

                    <button
                        class="btn btn-primary"
                        onclick="acceptRequest(${request.request_id})">

                        Accept

                    </button>

                    <button
                        class="btn btn-danger"
                        onclick="rejectRequest(${request.request_id})">

                        Reject

                    </button>

                </div>
            `;
        }


        return `
            <div class="request-card">

                <div class="request-top">

                    <div>

                        <h3>
                            ${request.crop_name}
                        </h3>

                        <p>
                            Purchase Request #${request.request_id}
                        </p>

                    </div>

                    <span class="status ${statusClass}">
                        ${request.status}
                    </span>

                </div>


                <div class="request-details">

                    <div class="detail-box">

                        <small>Quantity</small>

                        <strong>
                            ${request.requested_quantity}
                            ${request.quantity_unit}
                        </strong>

                    </div>


                    <div class="detail-box">

                        <small>Offered Price</small>

                        <strong>
                            ₹${request.offered_price_per_kg}/kg
                        </strong>

                    </div>


                    <div class="detail-box">

                        <small>Total Value</small>

                        <strong>
                            ₹${request.total_amount}
                        </strong>

                    </div>

                </div>


                ${
                    request.message
                        ? `
                            <p>
                                <strong>Buyer Message:</strong>
                                ${request.message}
                            </p>
                          `
                        : ""
                }


                ${
                    request.farmer_response
                        ? `
                            <p>
                                <strong>Your Response:</strong>
                                ${request.farmer_response}
                            </p>
                          `
                        : ""
                }


                ${actions}

            </div>
        `;

    }).join("");
}


// =========================================================
// ACCEPT
// =========================================================

async function acceptRequest(requestId) {

    const confirmed = confirm(
        "Accept this purchase request?"
    );

    if (!confirmed) return;


    await updateRequest(
        requestId,
        "accept"
    );
}


// =========================================================
// REJECT
// =========================================================

async function rejectRequest(requestId) {

    const confirmed = confirm(
        "Reject this purchase request?"
    );

    if (!confirmed) return;


    await updateRequest(
        requestId,
        "reject"
    );
}


// =========================================================
// UPDATE REQUEST
// =========================================================

async function updateRequest(
    requestId,
    action
) {

    try {

        const response = await fetch(
            `${API_URL}/api/farmer/purchase-requests/${requestId}/${action}`,
            {
                method: "PATCH",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Something went wrong"
            );
        }


        alert(data.message);

        loadPurchaseRequests();

    } catch (error) {

        alert(error.message);
    }
}


// =========================================================
// LOGOUT
// =========================================================

document
    .getElementById("logoutBtn")
    .addEventListener("click", function(event) {

        event.preventDefault();

        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("role");
        localStorage.removeItem("full_name");

        window.location.href = "login.html";
    });


// loadPurchaseRequests();

// const API_BASE = "http://localhost:8000";
// const token = localStorage.getItem("access_token");

// if (!token) {
//     window.location.href = "login.html";
// }


// -------------------------
// LOAD MY CROPS
// -------------------------

async function loadMyCrops() {

    const container = document.getElementById("myCrops");

    try {

        const response = await fetch(
            `${API_BASE}/api/farmer/crops`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Failed to load crops");
        }

        const crops = await response.json();

        if (!crops.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No crops listed yet</h3>
                    <p>Add your first crop to start receiving buyer requests.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = crops.map(crop => `
            <div class="crop-card">

                <div class="crop-card-header">
                    <h3>${crop.crop_name}</h3>

                    <span class="status-badge ${crop.status?.toLowerCase()}">
                        ${crop.status || "AVAILABLE"}
                    </span>
                </div>

                <p>
                    <strong>Quantity:</strong>
                    ${crop.quantity} ${crop.quantity_unit}
                </p>

                <p>
                    <strong>Quality:</strong>
                    Grade ${crop.quality_grade}
                </p>

                <p>
                    <strong>Expected Price:</strong>
                    ₹${crop.expected_price_per_kg}/kg
                </p>

                <p>
                    <strong>Location:</strong>
                    ${crop.city}, ${crop.district}
                </p>

                <p>
                    <strong>Harvest:</strong>
                    ${crop.harvest_date}
                </p>

            </div>
        `).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <p>Unable to load crops.</p>
        `;
    }
}


// -------------------------
// ADD CROP
// -------------------------

document.getElementById("cropForm").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const form = document.getElementById("cropForm");
        const formData = new FormData(form);

        try {

            const response = await fetch(
                `${API_BASE}/api/farmer/crops`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    },
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Failed to add crop");
                return;
            }

            alert("Crop listed successfully! 🌾");

            form.reset();

            hideAddCrop();

            loadMyCrops();

        } catch (error) {

            console.error(error);

            alert("Server error. Please try again.");
        }
    }
);


// -------------------------
// SHOW / HIDE ADD CROP
// -------------------------

function showAddCrop() {
    document.getElementById("addCropSection").style.display = "block";

    document.getElementById("addCropSection")
        .scrollIntoView({ behavior: "smooth" });
}

function hideAddCrop() {
    document.getElementById("addCropSection").style.display = "none";
}


// -------------------------
// INITIAL LOAD
// -------------------------

loadMyCrops();