function updateDate() {
  let date = new Date();
  let dateNow =
    date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }) +
    " " +
    date.toLocaleTimeString();
  let elements = document.querySelectorAll(".date-now");

  elements.forEach(function (element) {
    element.innerHTML = dateNow;
  });

  localStorage.setItem("lastDate", dateNow);
}

let storedDate = localStorage.getItem("lastDate");
if (storedDate) {
  let elements = document.querySelectorAll(".date-now");
  elements.forEach(function (element) {
    element.innerHTML = storedDate;
  });
}

setInterval(updateDate, 1000);
