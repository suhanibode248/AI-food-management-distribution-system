// Show alert when request is made
function requestFood() {
    alert("Food request sent successfully!");
}

// Auto hide success message after 3 sec
setTimeout(() => {
    let msg = document.getElementById("msg");
    if (msg) {
        msg.style.display = "none";
    }
}, 3000);

// Expiry check (basic frontend warning)
function checkExpiry(expiryTime) {
    let now = new Date();
    let expiry = new Date(expiryTime);

    if (expiry < now) {
        return "Expired ❌";
    } else {
        return "Available ✅";
    }
}

// Highlight expired food items
window.onload = function () {
    let items = document.querySelectorAll(".food-item");

    items.forEach(item => {
        let expiry = item.getAttribute("data-expiry");
        let status = checkExpiry(expiry);

        let statusTag = item.querySelector(".status");

        if (statusTag) {
            statusTag.innerText = status;
        }

        if (status.includes("Expired")) {
            item.style.background = "#ffe6e6";
        }
    });
};