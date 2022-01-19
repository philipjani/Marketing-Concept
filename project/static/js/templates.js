document.addEventListener("DOMContentLoaded", function () {
  let LOCATION = null;

  // button listeners
  document
    .querySelector("button[data-flag='fname']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTfnameTtT");
    });
  document
    .querySelector("button[data-flag='lname']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTlnameTtT");
    });
  document
    .querySelector("button[data-flag='age']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTageTtT");
    });
  document
    .querySelector("button[data-flag='address']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTaddressTtT");
    });
  document
    .querySelector("button[data-flag='city']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTcityTtT");
    });
  document
    .querySelector("button[data-flag='state']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTstateTtT");
    });
  document
    .querySelector("button[data-flag='zip']")
    .addEventListener("click", (e) => {
      e.preventDefault();
      add_var("TtTzipTtT");
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
