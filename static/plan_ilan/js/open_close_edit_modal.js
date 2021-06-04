function openRateModal(btn) {
    let modal = document.getElementById('rateModal_' + btn.id.split("_")[1]);
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
function closeRateModal(closeBtn) {
    let modal = document.getElementById('rateModal_' + closeBtn.id.split("_")[1]);
    modal.style.display = "none";
}
