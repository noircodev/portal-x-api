const setup = {
  initTypeaheadSearch: function () {
    const searchInput = document.getElementById("searchInput");
    const searchForm = document.getElementById("search-form");
    const searchCtn = document.getElementById("searchCtn");
    const clearBtn = document.getElementById("clearBtn");
    const searchIcon = document.getElementById("searchIcon");
    const backIcon = document.getElementById("backIcon");
    const heroSection = document.getElementById("heroSection");
    const eventsCtn = document.getElementById("eventsCtn");
    const footer = document.getElementById("footer");
    const pagination = document.getElementById("pagination");

    if (!searchInput || !searchForm) return;

    let originalTypedText = "";
    let searchResultsContainer = null;
    let hoveredSuggestion = null;
    let originalInputValue = "";
    let hasUserTyped = false;

    function highlightMatch(text, query) {
      if (!query) return text;
      const pattern = new RegExp(`(${query})`, "gi");
      return text.replace(pattern, '<span class="highlight">$1</span>');
    }

    function showSearchContainer() {
      searchCtn.classList.remove("hidden");
      setTimeout(() => {
        searchCtn.classList.remove("opacity-0", "translate-y-3");
      }, 10);

      searchIcon.classList.add("hidden");
      backIcon.classList.remove("hidden");

      if (window.innerWidth <= 767) {
        heroSection?.classList.add("hidden");
        eventsCtn?.classList.add("hidden");
        pagination?.classList.add("hidden");
        footer?.classList.add("hidden");
      }
    }

    function hideSearchContainer() {
      searchInput.blur(); // close keyboard

      searchCtn.classList.add("opacity-0", "translate-y-3");

      setTimeout(() => {
        searchCtn.classList.add("hidden");

        heroSection?.classList.remove("hidden");
        eventsCtn?.classList.remove("hidden");
        footer?.classList.remove("hidden");
        if (pagination) {
          pagination.classList.remove("hidden");
        }

        searchIcon.classList.remove("hidden");
        backIcon.classList.add("hidden");

        searchInput.value = "";
        clearBtn.classList.add("hidden");

        hasUserTyped = false;
        originalTypedText = "";
        originalInputValue = "";
        hoveredSuggestion = null;

        if (searchResultsContainer) {
          searchResultsContainer.innerHTML = "";
        }

        // optional scroll fix for mobile
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
      }, 300);
    }

    function createSearchResultsContainer() {
      if (searchResultsContainer) return searchResultsContainer;

      let searchInnerDiv =
        searchCtn.querySelector(".mt-\\[33px\\]") ||
        searchCtn.querySelector('div[class*="mt-[33px]"]') ||
        searchCtn.querySelector(".overflow-y-auto") ||
        searchCtn.querySelector("div div div");

      if (!searchInnerDiv) return null;

      searchResultsContainer = document.createElement("div");
      searchResultsContainer.id = "typeahead-results";
      searchResultsContainer.className = "w-full";

      searchInnerDiv.innerHTML = "";
      searchInnerDiv.appendChild(searchResultsContainer);

      return searchResultsContainer;
    }

    function createSuggestionHTML(data, index) {
      let iconSrc = "/static/home/assets/img/icons/recentSearch.svg";

      const label = highlightMatch(data.name, originalTypedText);

      return `
        <div class="suggestion-item flex items-center justify-between gap-[29px] md:gap-2 lg:gap-[29px] w-full mt-[22px] first:mt-0 cursor-pointer hover:bg-gray-100 hover:bg-opacity-10 rounded-lg p-2 transition-colors duration-200" 
             data-suggestion='${JSON.stringify(data)}' 
             data-index="${index}">
          <div class="flex items-center gap-[29px] md:gap-[6.8px] lg:gap-[29px] w-full">
            <img src="${iconSrc}" alt="search" class="md:w-[14.65px] md:h-[14.65px] lg:w-[42.9px] lg:h-[42.9px]" />
            <p class="font-medium text-[14.5px] font-GeneralSans w-full md:text-[10.46px] lg:text-[17.88px] md:font-jakarta md:font-medium md:line-clamp-1">
              ${label}
            </p>
          </div>
          <img src="/static/home/assets/img/icons/upArrow.svg" alt="" class="md:w-[14.65px] md:h-[14.65px] lg:w-[42.9px] lg:h-[42.9px]" />
        </div>
      `;
    }

    function renderSuggestions(suggestions) {
      const container = createSearchResultsContainer();
      if (!container) return;

      if (!hasUserTyped || !originalTypedText) {
        container.innerHTML = "";
        return;
      }

      const limited = suggestions.slice(0, 20);
      if (limited.length === 0) {
        container.innerHTML = `<div class="text-center py-8"><p class="font-jakarta font-medium text-sm text-gray-400">No results found</p></div>`;
        return;
      }

      container.innerHTML = limited
        .map((s, i) => createSuggestionHTML(s, i))
        .join("");

      container.querySelectorAll(".suggestion-item").forEach((el) => {
        el.addEventListener("click", function () {
          const suggestion = JSON.parse(this.dataset.suggestion);
          searchInput.value = suggestion.name || suggestion;
          showLoader();
          searchForm.submit();
        });

        el.addEventListener("mouseenter", function () {
          hoveredSuggestion = JSON.parse(this.dataset.suggestion);
          if (!originalInputValue) {
            originalInputValue = searchInput.value;
          }
          searchInput.value = hoveredSuggestion.name || hoveredSuggestion;
          this.classList.add("bg-gray-100", "bg-opacity-10");
        });

        el.addEventListener("mouseleave", function () {
          this.classList.remove("bg-gray-100", "bg-opacity-10");
          if (originalInputValue) {
            searchInput.value = originalInputValue;
          }
          hoveredSuggestion = null;
        });
      });
    }

    function performSearch(query) {
      if (!query || query.length < 1) {
        const container = createSearchResultsContainer();
        if (container) container.innerHTML = "";
        return;
      }

      fetch(`/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then((res) => res.json())
        .then((data) => {
          const seen = new Set();
          const filtered = data.filter((item) => {
            const key = item.name?.toLowerCase() || "";
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
          });
          renderSuggestions(filtered);
        })
        .catch(() => renderSuggestions([]));
    }

    function showLoader() {
      const loader = document.getElementById("page-loader");
      if (loader)
        loader.classList.remove("hidden"), loader.classList.add("flex");
    }

    searchInput.addEventListener("focus", () => {
      showSearchContainer();
      if (!hasUserTyped) {
        const container = createSearchResultsContainer();
        if (container) container.innerHTML = "";
      }
    });

    searchInput.addEventListener("input", function () {
      const query = this.value.trim();
      originalTypedText = query;
      hasUserTyped = true;
      originalInputValue = query;
      hoveredSuggestion = null;

      if (query) {
        clearBtn.classList.remove("hidden");
      } else {
        setTimeout(() => clearBtn.classList.add("hidden"), 100);
      }

      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => performSearch(query), 300);
    });

    clearBtn.addEventListener("click", () => {
      searchInput.value = "";
      searchInput.focus();
      clearBtn.classList.add("hidden");
      originalTypedText = "";
      originalInputValue = "";
      hasUserTyped = false;
      hoveredSuggestion = null;

      const container = createSearchResultsContainer();
      if (container) container.innerHTML = "";
    });

    backIcon.addEventListener("click", hideSearchContainer);

    searchInput.addEventListener("blur", () => {
      if (hoveredSuggestion && originalInputValue) {
        searchInput.value = originalInputValue;
      }
      setTimeout(() => {
        if (
          window.innerWidth > 767 &&
          !searchCtn.contains(document.activeElement)
        ) {
          searchCtn.classList.add("hidden");
          backIcon.classList.add("hidden");
          searchIcon.classList.remove("hidden");
        }
      }, 200);
    });

    searchForm.addEventListener("submit", (e) => {
      let query = searchInput.value.trim();
      if (hoveredSuggestion) {
        query = hoveredSuggestion.name || hoveredSuggestion;
        searchInput.value = query;
      }

      if (!query) {
        e.preventDefault();
      } else {
        showLoader();
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 767 || searchCtn.classList.contains("hidden")) {
        heroSection?.classList.remove("hidden");
        eventsCtn?.classList.remove("hidden");
        pagination?.classList.remove("hidden");
        footer?.classList.remove("hidden");
      } else {
        heroSection?.classList.add("hidden");
        eventsCtn?.classList.add("hidden");
        pagination?.classList.add("hidden");
        footer?.classList.add("hidden");
      }
    });

    window.addEventListener("popstate", () => {
      if (window.innerWidth <= 767 && !searchCtn.classList.contains("hidden")) {
        hideSearchContainer();
      }
    });

    searchInput.addEventListener("keydown", (e) => {
      const container = createSearchResultsContainer();
      if (!container) return;
      const suggestions = container.querySelectorAll(".suggestion-item");
      if (!suggestions.length) return;

      let currentIndex = -1;
      suggestions.forEach((el, i) => {
        if (el.classList.contains("bg-gray-100")) currentIndex = i;
      });

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (currentIndex >= 0) {
          suggestions[currentIndex].classList.remove(
            "bg-gray-100",
            "bg-opacity-10"
          );
        }
        currentIndex = Math.min(currentIndex + 1, suggestions.length - 1);
        suggestions[currentIndex].classList.add("bg-gray-100", "bg-opacity-10");
        const suggestion = JSON.parse(
          suggestions[currentIndex].dataset.suggestion
        );
        searchInput.value = suggestion.name || suggestion;
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (currentIndex >= 0) {
          suggestions[currentIndex].classList.remove(
            "bg-gray-100",
            "bg-opacity-10"
          );
        }
        currentIndex = Math.max(currentIndex - 1, -1);
        if (currentIndex >= 0) {
          suggestions[currentIndex].classList.add(
            "bg-gray-100",
            "bg-opacity-10"
          );
          const suggestion = JSON.parse(
            suggestions[currentIndex].dataset.suggestion
          );
          searchInput.value = suggestion.name || suggestion;
        } else {
          searchInput.value = originalInputValue;
        }
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (currentIndex >= 0) {
          const suggestion = JSON.parse(
            suggestions[currentIndex].dataset.suggestion
          );
          searchInput.value = suggestion.name || suggestion;
          showLoader();
          searchForm.submit();
        }
      }
    });
  },

  initFlatpickr: function () {
    if (document.querySelector("#start_date")) {
      flatpickr("#start_date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        minDate: "today",
        disableMobile: true,
        theme: "dark",
      });
    }
  },

  initImageUploader: function () {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("event-image");
    const imgView = document.getElementById("img-view");
    const defaultIcon = document.getElementById("default-icon");
    const defaultText = document.getElementById("default-text");
    const defaultSize = document.getElementById("default-size");
    const imageError = document.getElementById("image-error"); // Corresponds to 'errorMessage' in your template JS

    // Ensure all required elements exist
    if (
      !dropArea ||
      !fileInput ||
      !imgView ||
      !defaultIcon ||
      !defaultText ||
      !defaultSize ||
      !imageError
    ) {
      console.error("One or more image uploader elements are missing.");
      return;
    }

    const MAX_FILE_SIZE = 1048576; // 1MB in bytes

    /**
     * Resets the image preview area to its default state (showing upload prompt).
     */
    function resetToDefault() {
      imgView.style.backgroundImage = "";
      defaultIcon.classList.remove("hidden");
      defaultText.classList.remove("hidden");
      defaultSize.classList.remove("hidden");
      fileInput.value = ""; // Clear the file input
      imageError.classList.add("hidden"); // Hide any error messages
    }

    /**
     * Validates the selected file and displays a preview or an error message.
     * @param {File} file - The file to validate and preview.
     */
    function handleFileSelect(file) {
      imageError.classList.add("hidden"); // Hide previous errors

      if (!file) {
        resetToDefault();
        return;
      }

      if (!file.type.startsWith("image/")) {
        imageError.textContent = "Please upload an image file (PNG, JPG).";
        imageError.classList.remove("hidden");
        resetToDefault();
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        imageError.textContent = "File size must be less than 1MB.";
        imageError.classList.remove("hidden");
        resetToDefault();
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        // Hide default content
        defaultIcon.classList.add("hidden");
        defaultText.classList.add("hidden");
        defaultSize.classList.add("hidden");
        // Set image as background
        imgView.style.backgroundImage = `url(${e.target.result})`;
      };
      reader.readAsDataURL(file);
    }

    // --- Event Listeners ---

    // Handle file selection via input click
    fileInput.addEventListener("change", (e) => {
      handleFileSelect(e.target.files[0]);
    });

    // Handle drag over event
    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.classList.add("border-cyan-500", "bg-gray-800/30"); // Use your hover styles
    });

    // Handle drag leave event
    dropArea.addEventListener("dragleave", () => {
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
    });

    // Handle drop event
    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
      handleFileSelect(e.dataTransfer.files[0]);
      // Assign the dropped file to the input's files list for form submission
      if (
        e.dataTransfer.files[0] &&
        e.dataTransfer.files[0].size <= MAX_FILE_SIZE &&
        e.dataTransfer.files[0].type.startsWith("image/")
      ) {
        fileInput.files = e.dataTransfer.files;
      }
    });

    // Initialize: Ensure the area is in its default state when loaded
    resetToDefault();
  },

  initImageUploader: function () {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("event-image");
    const imgView = document.getElementById("img-view");
    const defaultIcon = document.getElementById("default-icon");
    const defaultText = document.getElementById("default-text");
    const defaultSize = document.getElementById("default-size");
    const imageError = document.getElementById("image-error");
    const removeButton = document.getElementById("remove-image"); // New: Remove button element

    // Ensure all required elements exist
    if (
      !dropArea ||
      !fileInput ||
      !imgView ||
      !defaultIcon ||
      !defaultText ||
      !defaultSize ||
      !imageError ||
      !removeButton
    ) {
      console.error(
        "One or more image uploader elements are missing. Ensure 'remove-image' button exists."
      );
      return;
    }

    const MAX_FILE_SIZE = 1048576; // 1MB in bytes

    /**
     * Resets the image preview area to its default state (showing upload prompt).
     */
    function resetToDefault() {
      imgView.style.backgroundImage = "";
      // Remove background size style when resetting to ensure it doesn't affect default view
      imgView.style.backgroundSize = "";
      defaultIcon.classList.remove("hidden");
      defaultText.classList.remove("hidden");
      defaultSize.classList.remove("hidden");
      removeButton.classList.add("hidden"); // Hide remove button
      fileInput.value = ""; // Clear the file input
      imageError.classList.add("hidden"); // Hide any error messages
    }

    /**
     * Validates the selected file and displays a preview or an error message.
     * @param {File} file - The file to validate and preview.
     */
    function handleFileSelect(file) {
      imageError.classList.add("hidden"); // Hide previous errors

      if (!file) {
        resetToDefault();
        return;
      }

      if (!file.type.startsWith("image/")) {
        imageError.textContent = "Please upload an image file (PNG, JPG).";
        imageError.classList.remove("hidden");
        resetToDefault(); // Reset on invalid file type
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        imageError.textContent = "File size exceeds 1MB limit.";
        imageError.classList.remove("hidden");
        resetToDefault(); // Reset and prevent upload if file is too large
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        // Hide default content
        defaultIcon.classList.add("hidden");
        defaultText.classList.add("hidden");
        defaultSize.classList.add("hidden");
        // Set image as background
        imgView.style.backgroundImage = `url(${e.target.result})`;
        // Ensure the image covers the full width
        imgView.style.backgroundSize = "contain"; // Change to "cover" if you prefer it to fill and crop
        imgView.style.backgroundRepeat = "no-repeat"; // Ensure no tiling
        imgView.style.backgroundPosition = "center"; // Center the image

        removeButton.classList.remove("hidden"); // Show remove button
      };
      reader.readAsDataURL(file);
    }

    // --- Event Listeners ---

    // Handle file selection via input change
    fileInput.addEventListener("change", (e) => {
      handleFileSelect(e.target.files[0]);
    });

    // Handle drag over event
    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.classList.add("border-cyan-500", "bg-gray-800/30");
    });

    // Handle drag leave event
    dropArea.addEventListener("dragleave", () => {
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
    });

    // Handle drop event
    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
      const droppedFile = e.dataTransfer.files[0];
      handleFileSelect(droppedFile); // Validate and preview the dropped file

      // If the file is valid after handleFileSelect, assign it to the input for form submission
      if (
        droppedFile &&
        droppedFile.size <= MAX_FILE_SIZE &&
        droppedFile.type.startsWith("image/")
      ) {
        fileInput.files = e.dataTransfer.files;
      } else {
        // If the dropped file is invalid, clear the input's files to prevent submission of invalid data
        fileInput.value = "";
      }
    });

    // Handle click on remove button
    removeButton.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevent event bubbling to dropArea (which would open file input)
      resetToDefault();
    });

    // Initialize: Ensure the area is in its default state when loaded
    resetToDefault();
  },

  initMobileMenu: function () {
    const openMenu = document.getElementById("openMenu");
    const closeMenu = document.getElementById("closeMenu");
    const navBar = document.getElementById("navBar");
    const dropdownMenu = document.getElementById("dropdownMenu");

    if (!openMenu || !closeMenu) return;

    openMenu.addEventListener("click", () => {
      openMenu.classList.add("hidden");
      closeMenu.classList.remove("hidden");
      navBar.classList.add("h-dvh");
      dropdownMenu.classList.remove("hidden");
    });

    closeMenu.addEventListener("click", () => {
      openMenu.classList.remove("hidden");
      closeMenu.classList.add("hidden");
      navBar.classList.remove("h-dvh");
      dropdownMenu.classList.add("hidden");
    });
  },

  init: function () {
    this.initTypeaheadSearch();
    this.initFlatpickr();
    // this.initImageUploader();
    this.initMobileMenu();
  },
};

document.addEventListener("DOMContentLoaded", function () {
  setup.init();
});
