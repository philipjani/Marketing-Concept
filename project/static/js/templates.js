document.addEventListener("DOMContentLoaded", function () {
  let LOCATION = null;

  // button listeners
  document
    .querySelector("button[data-flag='fname']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttfnametttttt");
    });
  document
    .querySelector("button[data-flag='lname']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttlnametttttt");
    });
  document
    .querySelector("button[data-flag='age']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttagetttttt");
    });
  document
    .querySelector("button[data-flag='address']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttaddresstttttt");
    });
  document
    .querySelector("button[data-flag='city']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttcitytttttt");
    });
  document
    .querySelector("button[data-flag='state']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttstatetttttt");
    });
  document
    .querySelector("button[data-flag='zip']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("ttttttziptttttt");
    });

  // get caret location listeners
  document.getElementById("message").addEventListener("keyup", function () {
    LOCATION = this.selectionStart;
  });
  document.getElementById("message").addEventListener("click", function () {
    LOCATION = this.selectionStart;
  });

  // insert function
  function add_var(str) {
    let el = document.getElementById("message");
    let inserted = `${el.value.slice(0, LOCATION)}${str}${el.value.slice(
      LOCATION
    )}`;
    el.value = inserted;
    el.focus();
    el.selectionEnd = LOCATION + str.length;
  }
});
