const API_BASE = "http://localhost:8000";

const token = localStorage.getItem("access_token");


// =========================
// AVAILABLE CROPS
// =========================

async function loadAvailableCrops() {

    const container = document.getElementById("availableCrops");

    try {

        const response = await fetch(
            `${API_BASE}/api/buyer/crops`,
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
                    <h3>No crops available</h3>
                    <p>New farmer listings will appear here.</p>
                </div>
            `;

            return;
        }

        document.getElementById("openRequestCount").textContent =
            crops.length;

        container.innerHTML = crops.map(crop => `

            <div class="crop-card">

                <h3>${crop.crop_name}</h3>

                <p>
                    <strong>Quantity:</strong>
                    ${crop.quantity} ${crop.quantity_unit}
                </p>

                <p>
                    <strong>Quality:</strong>
                    Grade ${crop.quality_grade}
                </p>

                <p>
                    <strong>Price:</strong>
                    ₹${crop.expected_price_per_kg}/kg
                </p>

                <p>
                    <strong>Location:</strong>
                    ${crop.city}, ${crop.district}
                </p>

                <button
                    class="btn btn-primary"
                    onclick="sendPurchaseRequest(${crop.id})">
                    Send Purchase Request
                </button>

            </div>

        `).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load crops.</p>";
    }
}


// =========================
// PURCHASE REQUEST
// =========================

async function sendPurchaseRequest(cropId) {

    const quantity = prompt("Enter required quantity:");

    if (!quantity || Number(quantity) <= 0) {
        return;
    }

    const price = prompt("Enter offered price per kg:");

    if (!price || Number(price) <= 0) {
        return;
    }

    const message = prompt(
        "Message to farmer (optional):"
    ) || "";


    try {

        const response = await fetch(
            `${API_BASE}/api/buyer/purchase-requests`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    crop_id: cropId,
                    requested_quantity: Number(quantity),
                    offered_price_per_kg: Number(price),
                    message: message
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Request failed");
            return;
        }

        alert("Purchase request sent successfully ✅");

    } catch (error) {

        console.error(error);

        alert("Server error");
    }
}


// =========================
// QUALITY CHECKED REQUESTS
// =========================

async function loadQualityRequests() {

    const container =
        document.getElementById("qualityRequests");

    try {

        const response = await fetch(
            `${API_BASE}/api/buyer/quality-checked-requests`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Failed");
        }

        const requests = await response.json();

        document.getElementById("qualityCount").textContent =
            requests.length;

        if (!requests.length) {

            container.innerHTML = `
                <div class="empty-state">
                    <p>No quality-checked purchases yet.</p>
                </div>
            `;

            return;
        }


        container.innerHTML = requests.map(item => `

            <div class="dashboard-card">

                <h3>${item.crop_name}</h3>

                <p>
                    <strong>Requested:</strong>
                    ${item.requested_quantity}
                </p>

                <p>
                    <strong>Approved:</strong>
                    ${item.quantity_approved}
                </p>

                <p>
                    <strong>Quality:</strong>
                    Grade ${item.quality_grade}
                </p>

                <p>
                    <strong>Remarks:</strong>
                    ${item.remarks || "None"}
                </p>

                <button
                    class="btn btn-primary"
                    onclick="confirmPurchase(${item.request_id})">
                    Confirm Purchase
                </button>

            </div>

        `).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load quality checks.</p>";
    }
}


// =========================
// CONFIRM PURCHASE
// =========================

async function confirmPurchase(requestId) {

    if (!confirm(
        "Confirm this purchase after quality inspection?"
    )) {
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE}/api/buyer/purchase-requests/${requestId}/confirm`,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Confirmation failed");
            return;
        }

        alert(
            `Purchase confirmed!\nAmount: ₹${data.total_amount}`
        );

        loadQualityRequests();

    } catch (error) {

        console.error(error);

        alert("Server error");
    }
}


// =========================
// ROUTE OPTIMIZATION
// =========================

function optimizeRoute() {

    document.getElementById("routeResult").innerHTML = `
        <div class="dashboard-card">

            <h3>Route Optimization</h3>

            <p>
                Route optimization API will be connected here.
            </p>

            <p>
                Farmers will be arranged according to
                the shortest pickup route.
            </p>

        </div>
    `;
}


// =========================
// LOGOUT
// =========================

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";
}


// =========================
// INITIAL LOAD
// =========================

loadAvailableCrops();
loadQualityRequests();