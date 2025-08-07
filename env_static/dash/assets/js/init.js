const setup = {
  initSystemStatsCharts: function () {
    const $cpuCanvas = $("#cpuChart");
    const $ramCanvas = $("#ramChart");
    const $swapCanvas = $("#swapChart");

    if (!$cpuCanvas.length || !$ramCanvas.length || !$swapCanvas.length) return;

    const MAX_POINTS = 60;

    const cpuChart = new Chart($cpuCanvas[0].getContext("2d"), {
      type: "line",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        animation: {
          duration: 800,
          easing: "easeInOutQuart",
        },
        interaction: {
          mode: "nearest",
          axis: "x",
          intersect: false,
        },
        plugins: {
          legend: { position: "top", labels: { color: "#eee" } },
          tooltip: {
            backgroundColor: "#333",
            titleColor: "#fff",
            bodyColor: "#ddd",
            borderColor: "#555",
            borderWidth: 1,
          },
        },
        elements: {
          line: { tension: 0.3, borderWidth: 2 },
          point: { radius: 0, hoverRadius: 2 },
        },
        scales: {
          x: { ticks: { color: "#ccc" }, grid: { display: false } },
          y: {
            beginAtZero: true,
            max: 100,
            ticks: { color: "#ccc" },
            grid: { display: false },
          },
        },
      },
    });

    const ramChart = new Chart($ramCanvas[0].getContext("2d"), {
      type: "bar",
      data: {
        labels: ["RAM"],
        datasets: [
          {
            label: "Used",
            data: [0],
            backgroundColor: "#f4c22b",
          },
          {
            label: "Available",
            data: [0],
            backgroundColor: "#f4c22b55",
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        animation: { duration: 500, easing: "easeOutCubic" },
        plugins: {
          legend: { position: "top", labels: { color: "#eee" } },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const chart = ctx.chart;
                const datasets = chart.data.datasets;
                const used = datasets[0].data[0];
                const available = datasets[1].data[0];
                const total = used + available;
                const percent = ((ctx.raw / total) * 100).toFixed(1);
                return `${ctx.dataset.label}: ${formatBytes(
                  ctx.raw
                )} (${percent}%)`;
              },
            },
            backgroundColor: "#333",
            titleColor: "#fff",
            bodyColor: "#ddd",
          },
        },
        elements: {
          bar: {
            borderRadius: 4,
            barThickness: 6,
          },
        },
        aspectRatio: 6,
        scales: {
          x: {
            stacked: true,
            ticks: {
              color: "#ccc",
              callback: (v) => formatBytes(v),
            },
            grid: { display: false },
          },
          y: {
            stacked: true,
            ticks: { color: "#ccc" },
            grid: { display: false },
          },
        },
      },
    });

    const swapChart = new Chart($swapCanvas[0].getContext("2d"), {
      type: "bar",
      data: {
        labels: ["Swap"],
        datasets: [
          {
            label: "Used",
            data: [0],
            backgroundColor: "#04a9f5",
          },
          {
            label: "Free",
            data: [0],
            backgroundColor: "#04a9f555",
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        animation: { duration: 500, easing: "easeOutCubic" },
        plugins: {
          legend: { position: "top", labels: { color: "#eee" } },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const chart = ctx.chart;
                const datasets = chart.data.datasets;
                const used = datasets[0].data[0];
                const free = datasets[1].data[0];
                const total = used + free;
                const percent = ((ctx.raw / total) * 100).toFixed(1);
                return `${ctx.dataset.label}: ${formatBytes(
                  ctx.raw
                )} (${percent}%)`;
              },
            },
            backgroundColor: "#333",
            titleColor: "#fff",
            bodyColor: "#ddd",
          },
        },
        elements: {
          bar: {
            borderRadius: 4,
            barThickness: 5,
          },
        },
        aspectRatio: 6,
        scales: {
          x: {
            stacked: true,
            ticks: {
              color: "#ccc",
              callback: (v) => formatBytes(v),
            },
            grid: { display: false },
          },
          y: {
            stacked: true,
            ticks: { color: "#ccc" },
            grid: { display: false },
          },
        },
      },
    });

    function formatBytes(bytes) {
      if (bytes >= 1 << 30) return (bytes / (1 << 30)).toFixed(2) + " GB";
      if (bytes >= 1 << 20) return (bytes / (1 << 20)).toFixed(2) + " MB";
      return (bytes / (1 << 10)).toFixed(2) + " KB";
    }

    function updateCharts(data) {
      const now = new Date(data.timestamp * 1000);
      const timestamp =
        now.toLocaleTimeString("en-GB") + "." + now.getMilliseconds();

      if (cpuChart.data.datasets.length === 0) {
        data.cpu.forEach((_, i) => {
          cpuChart.data.datasets.push({
            label: `CPU ${i + 1}`,
            data: [],
            borderColor: `hsl(${i * 40}, 100%, 60%)`,
            fill: false,
          });
        });
      }

      cpuChart.data.labels.push(timestamp);
      if (cpuChart.data.labels.length > MAX_POINTS)
        cpuChart.data.labels.shift();

      cpuChart.data.datasets.forEach((ds, i) => {
        ds.data.push(data.cpu[i]);
        if (ds.data.length > MAX_POINTS) ds.data.shift();
      });
      cpuChart.update("none");

      ramChart.data.datasets[0].data = [data.memory.used];
      ramChart.data.datasets[1].data = [data.memory.available];
      ramChart.update();

      swapChart.data.datasets[0].data = [data.swap.used];
      swapChart.data.datasets[1].data = [data.swap.free];
      swapChart.update();
    }

    async function fetchStats() {
      try {
        const res = await fetch("/accounts/system/stats/");
        const json = await res.json();
        updateCharts(json);
      } catch (e) {
        console.error("Failed to fetch:", e);
      }
    }

    fetchStats();
    setInterval(fetchStats, 2000);
  },

  initDatePickers: function () {
    const selectors = ["#start_date", "#end_date"];

    selectors.forEach((selector) => {
      const el = document.querySelector(selector);
      if (el) {
        flatpickr(el, {
          altInput: true,
          altFormat: "F j, Y",
          dateFormat: "Y-m-d",
          defaultDate: el.value || null,
          minDate: "today",
          disableMobile: true,
          theme: "dark",
        });
      }
    });
  },

  initUploadAreaHandler: function () {
    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");
    const previewContainer = document.getElementById("previewContainer");
    const previewImage = document.getElementById("previewImage");
    const removeBtn = document.getElementById("removeBtn");
    const fileInfo = document.getElementById("fileInfo");
    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");
    const errorMessage = document.getElementById("errorMessage");
    const placeholderImage = document.getElementById("placeholderImage");

    if (!uploadArea || !fileInput || !previewImage) return;

    let selectedFile = null;

    uploadArea.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => handleFile(e.target.files[0]));

    uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadArea.classList.add("dragover");
    });

    uploadArea.addEventListener("dragleave", () => {
      uploadArea.classList.remove("dragover");
    });

    uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      uploadArea.classList.remove("dragover");
      const file = e.dataTransfer.files[0];
      handleFile(file);
    });

    removeBtn?.addEventListener("click", (e) => {
      e.stopPropagation();
      removeImage();
    });

    function handleFile(file) {
      if (!file) return;

      const validTypes = ["image/png", "image/jpg", "image/jpeg"];
      if (!validTypes.includes(file.type))
        return showError("Please select a PNG or JPG image file.");

      if (file.size > 5 * 1024 * 1024)
        return showError("File size must be less than 5MB.");

      selectedFile = file;
      hideError();

      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer?.classList.add("show");
        uploadArea.style.display = "none";
        placeholderImage?.style.setProperty("display", "none");
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo?.style.setProperty("display", "flex");
      };
      reader.readAsDataURL(file);
    }

    function removeImage() {
      selectedFile = null;
      previewContainer?.classList.remove("show");
      uploadArea.style.display = "block";
      fileInfo?.style.setProperty("display", "none");
      fileInput.value = "";
      placeholderImage?.style.setProperty("display", "block");
      hideError();
    }

    function showError(message) {
      errorMessage.textContent = message;
      errorMessage.classList.add("show");
      setTimeout(hideError, 5000);
    }

    function hideError() {
      errorMessage.classList.remove("show");
    }

    function formatFileSize(bytes) {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }
  },

  initSelect2Inputs: function () {
    if ($.fn.select2) {
      $(".select2-input").select2({
        // theme: "bootstrap-5",
        theme: "classic",
        width: "100%",
        placeholder: "Select an option",
        allowClear: true,
        minimumResultsForSearch: 10,
      });
    }
  },

  initSearchHighlight: function () {
    const context = document.querySelector("#eventContainer");
    highlights = document.getElementById("searchKeywords");
    if (!context || !highlights) return;
    const query = highlights.value.trim();
    if (!query) return;

    const instance = new Mark(context);
    instance.mark(query.split(/\s+/));
  },

  init: function () {
    this.initSystemStatsCharts();

    this.initDatePickers();
    this.initUploadAreaHandler();
    this.initSelect2Inputs();
    this.initSearchHighlight();
  },
};

document.addEventListener("DOMContentLoaded", function () {
  setup.init();
});
