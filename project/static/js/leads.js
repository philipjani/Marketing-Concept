document.addEventListener("DOMContentLoaded", function () {
  // select all button
  const check = document.querySelectorAll("input[id='select']");
  for (let i = 0; i < check.length; i++) {
    check[i].checked = false;
  }
  document.querySelector("[data-flag='select-all']").onclick = function () {
    let checkboxes = document.querySelectorAll("[data-click]");
    for (let checkbox of checkboxes) {
      checkbox.checked = this.checked;
    }
  };
  // select all leads attached to clicked address
  const address_checkboxes = document.querySelectorAll("[data-click='address'");
  for (let i = 0; i < address_checkboxes.length; i++) {
    address_checkboxes[i].addEventListener("click", function () {
      const id = address_checkboxes[i].getAttribute("data-pair");
      const attached = document.querySelectorAll(`input[data-pair="${id}"]`);
      for (const lead of attached) {
        lead.checked = address_checkboxes[i].checked;
      }
    });
  }
  // make sure that the address is always checked when an attached lead is checked
  // and make sure that the address is never selected without an attached lead
  const lead_checkboxes = document.querySelectorAll("[data-click='lead'");
  for (let i = 0; i < lead_checkboxes.length; i++) {
    lead_checkboxes[i].addEventListener("click", function () {
      const id = lead_checkboxes[i].getAttribute("data-pair");
      const address = document.querySelector(
        `input[data-pair="${id}"][data-click="address"]`
      );
      let leads = document.querySelectorAll(
        `input[data-pair="${id}"][data-click="lead"]`
      );
      const test = Array.from(leads, (i) => i.checked);
      if (none(test)) {
        address.checked = false;
      } else if (this.checked) {
        address.checked = true;
      }
    });
  }
});
// helper function
function none(iterable) {
  for (var index = 0; index < iterable.length; index++) {
    if (!!iterable[index]) return false;
  }
  return true;
}
