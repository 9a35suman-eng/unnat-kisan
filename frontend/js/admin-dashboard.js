const API_BASE = "https://unnat-kisan.onrender.com";

const token = localStorage.getItem("access_token");

// -------------------------
// LOAD PENDING BUYERS
// -------------------------

async function loadPendingBuyers() {
  const container = document.getElementById("pendingBuyers");

  try {
    const response = await fetch(`${API_BASE}/api/admin/bulk-buyers/pending`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load buyers");
    }

    const buyers = await response.json();

    document.getElementById("pendingBuyerCount").textContent = buyers.length;

    if (buyers.length === 0) {
      container.innerHTML = `
                <div class="empty-state">
                    <h3>No Pending Buyers</h3>
                    <p>All bulk buyers have been reviewed.</p>
                </div>
            `;

      return;
    }

    container.innerHTML = buyers
      .map(
        (buyer) => `

            <div class="dashboard-card buyer-verification-card">

                <h3>${buyer.business_name}</h3>

                <p>
                    <strong>Contact:</strong>
                    ${buyer.contact_person}
                </p>

                <p>
                    <strong>Business Type:</strong>
                    ${buyer.business_type}
                </p>

                <p>
                    <strong>Product:</strong>
                    ${buyer.product_category}
                </p>

                <p>
                    <strong>Monthly Requirement:</strong>
                    ${buyer.monthly_requirement}
                </p>

                <p>
                    <strong>License:</strong>
                    ${buyer.license_number}
                </p>

                ${
                  buyer.license_photo
                    ? `
                        <p>
                            <a
                                href="${API_BASE}/${buyer.license_photo}"
                                target="_blank"
                            >
                                📄 View License
                            </a>
                        </p>
                    `
                    : ""
                }

                <div class="card-actions">

                    <button
                        class="btn btn-primary"
                        onclick="approveBuyer(${buyer.id})">
                        Approve
                    </button>

                    <button
                        class="btn btn-secondary"
                        onclick="rejectBuyer(${buyer.id})">
                        Reject
                    </button>

                </div>

            </div>

        `,
      )
      .join("");
  } catch (error) {
    console.error(error);

    container.innerHTML = `
            <p>Unable to load pending buyers.</p>
        `;
  }
}

// -------------------------
// APPROVE
// -------------------------

async function approveBuyer(buyerId) {
  if (!confirm("Approve this bulk buyer?")) {
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/api/admin/bulk-buyers/${buyerId}/approve`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Approval failed");
      return;
    }

    alert("Bulk buyer approved successfully ✅");

    loadPendingBuyers();
  } catch (error) {
    console.error(error);

    alert("Server error");
  }
}

// -------------------------
// REJECT
// -------------------------

async function rejectBuyer(buyerId) {
  const reason = prompt("Enter rejection reason:");

  if (!reason) {
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/api/admin/bulk-buyers/${buyerId}/reject?rejection_reason=${encodeURIComponent(reason)}`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Rejection failed");
      return;
    }

    alert("Bulk buyer rejected");

    loadPendingBuyers();
  } catch (error) {
    console.error(error);

    alert("Server error");
  }
}

// -------------------------
// LOGOUT
// -------------------------

function logout() {
  localStorage.removeItem("access_token");

  window.location.href = "login.html";
}

// -------------------------
// INITIAL LOAD
// -------------------------

loadPendingBuyers();

async function loadPendingPayments() {
  const container = document.getElementById("pendingPayments");

  try {
    const response = await fetch(`${API_BASE}/api/admin/payments/pending`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load payments");
    }

    const payments = await response.json();

    document.getElementById("paymentCount").textContent = payments.length;

    if (payments.length === 0) {
      container.innerHTML = `
                <div class="empty-state">
                    <h3>No Pending Payments</h3>
                    <p>There are no payments waiting for verification.</p>
                </div>
            `;

      return;
    }

    container.innerHTML = payments
      .map(
        (payment) => `

            <div class="dashboard-card">

                <h3>Order #${payment.order_id}</h3>

                <p>
                    <strong>Amount:</strong>
                    ₹${payment.amount}
                </p>

                <p>
                    <strong>Payment Method:</strong>
                    ${payment.payment_method || "Not specified"}
                </p>

                ${
                  payment.payment_proof
                    ? `
                        <p>
                            <a
                                href="${API_BASE}/${payment.payment_proof}"
                                target="_blank">
                                📄 View Payment Proof
                            </a>
                        </p>
                    `
                    : ""
                }

                <div class="card-actions">

                    <button
                        class="btn btn-primary"
                        onclick="verifyPayment(${payment.payment_id})">
                        Verify Payment
                    </button>

                    <button
                        class="btn btn-secondary"
                        onclick="rejectPayment(${payment.payment_id})">
                        Reject
                    </button>

                </div>

            </div>

        `,
      )
      .join("");
  } catch (error) {
    console.error(error);

    container.innerHTML = "<p>Unable to load pending payments.</p>";
  }
}

async function verifyPayment(paymentId) {
  if (!confirm("Verify this payment?")) {
    return;
  }

  const response = await fetch(
    `${API_BASE}/api/admin/payments/${paymentId}/verify`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Verification failed");
    return;
  }

  alert("Payment verified successfully ✅");

  loadPendingPayments();
}

async function rejectPayment(paymentId) {
  const reason = prompt("Enter rejection reason:");

  if (!reason) {
    return;
  }

  const response = await fetch(
    `${API_BASE}/api/admin/payments/${paymentId}/reject?reason=${encodeURIComponent(reason)}`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Rejection failed");
    return;
  }

  alert("Payment rejected");

  loadPendingPayments();
}
