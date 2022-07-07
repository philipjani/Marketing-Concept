document.addEventListener("DOMContentLoaded", function () {
  const check = document.querySelectorAll("input[id='select']");
  for (let i = 0; i < check.length; i++) {
    check[i].checked = false;
  }

  document.querySelector("[data-flag='select-addresses']").onclick =
    function () {
      var checkboxes = document.querySelectorAll("[data-click=select-skip]");
      for (var checkbox of checkboxes) {
        checkbox.checked = this.checked;
      }
    };
  document.querySelector("[data-flag='select-leads']").onclick = function () {
    var checkboxes = document.querySelectorAll("[data-click=select-sms]");
    for (var checkbox of checkboxes) {
      checkbox.checked = this.checked;
    }
  };
  const tbut = document.querySelector("input[data-flag='template_button']");
  tbut.addEventListener("click", () => {
    let ids = [];
    for (let i = 0; i < check.length; i++) {
      if (check[i].checked) {
        ids.push(check[i].value);
      }
    }
    console.log(ids);
  });
});
