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
    let isSubmitting = false; // Add flag to prevent multiple submissions
    let searchTimeout = null; // Move timeout to outer scope

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
      searchInput.blur();

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
        isSubmitting = false; // Reset submission flag

        if (searchResultsContainer) {
          searchResultsContainer.innerHTML = "";
        }

        // Clear any pending search timeout
        if (searchTimeout) {
          clearTimeout(searchTimeout);
          searchTimeout = null;
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
        <div class="suggestion-item flex items-center justify-between gap-[29px] md:gap-2 lg:gap-[29px] w-full mt-0 cursor-pointer hover:bg-gray-100 hover:bg-opacity-10 rounded-lg p-2 transition-colors duration-200" 
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

    function createNoResultsHTML() {
      return `
        <div class="text-center py-8 px-4">
          <div class="flex flex-col items-center justify-center gap-4">
            <div class="place-items-center">
              <img src="/static/home/assets/img/icons/noEvent.png" alt="No events found" class="w-12 h-12 md:w-16 md:h-16 opacity-50" />
            </div>
            <div class="font-jakarta flex flex-col gap-2">
              <p class="text-lg font-bold text-(--primary-300) md:text-xl">
                Oooops! No Event for Now
              </p>
              <p class="text-white text-sm leading-relaxed md:text-base opacity-75">
                No events are available, but this aggregator helps you
                connect with like-minded individuals.
              </p>
            </div>
          </div>
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

      const limited = suggestions.slice(0, 15);

      if (limited.length === 0) {
        container.innerHTML = createNoResultsHTML();
        return;
      }

      container.innerHTML = limited
        .map((s, i) => createSuggestionHTML(s, i))
        .join("");

      // Add event listeners to suggestions
      container.querySelectorAll(".suggestion-item").forEach((el) => {
        el.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();

          if (isSubmitting) return; // Prevent multiple submissions

          const suggestion = JSON.parse(this.dataset.suggestion);
          searchInput.value = suggestion.name || suggestion;
          submitSearchForm();
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
      if (loader) {
        loader.classList.remove("hidden");
        loader.classList.add("flex");
      }
    }

    function submitSearchForm() {
      if (isSubmitting) return; // Prevent multiple submissions

      isSubmitting = true;
      showLoader();

      // Use requestAnimationFrame to ensure loader is shown before form submission
      requestAnimationFrame(() => {
        try {
          searchForm.submit();
        } catch (error) {
          console.error("Form submission error:", error);
          isSubmitting = false;
        }
      });
    }

    // Event Listeners
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

      // Clear existing timeout
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }

      // Set new timeout
      searchTimeout = setTimeout(() => performSearch(query), 300);
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
      e.preventDefault(); // Always prevent default to control submission

      let query = searchInput.value.trim();
      if (hoveredSuggestion) {
        query = hoveredSuggestion.name || hoveredSuggestion;
        searchInput.value = query;
      }

      if (!query) {
        return; // Don't submit empty queries
      }

      submitSearchForm();
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
          submitSearchForm();
        } else {
          // Submit current input value
          submitSearchForm();
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
  initSearchHighlight: function () {
    const context = document.querySelector("#eventContainer");
    highlights = document.getElementById("searchKeywords");
    if (!context || !highlights) return;
    const query = highlights.value.trim();
    if (!query) return;

    const instance = new Mark(context);
    instance.mark(query.split(/\s+/));
  },

  initMobileMenuToggle: function () {
    const openMenu = document.getElementById("openMenu");
    const closeMenu = document.getElementById("closeMenu");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const closeBanner = document.getElementById("closeBanner");
    const banner = document.getElementById("banner");
    const activeLinks = document.querySelectorAll(".nav-link-active");

    // --- Close Banner ---
    if (closeBanner && banner) {
      closeBanner.addEventListener("click", () => {
        banner.classList.add("md:hidden");
        document.body.classList.remove("lg:pt-[148px]");
        document.body.classList.add("lg:pt-[100px]");
        document.body.classList.remove("md:pt-[77px]");
        document.body.classList.add("md:pt-[52px]");
      });
    }

    // --- Mobile Menu Open ---
    if (openMenu && closeMenu && dropdownMenu) {
      openMenu.addEventListener("click", () => {
        dropdownMenu.classList.remove("hidden");

        requestAnimationFrame(() => {
          dropdownMenu.classList.remove("opacity-0", "-translate-y-4");
          dropdownMenu.classList.add("opacity-100", "translate-y-0");
          openMenu.classList.add("hidden");
          closeMenu.classList.remove("hidden");
        });

        document.body.classList.add("overflow-hidden");
      });

      // --- Mobile Menu Close ---
      closeMenu.addEventListener("click", () => {
        dropdownMenu.classList.add("opacity-0", "-translate-y-4");
        dropdownMenu.classList.remove("opacity-100", "translate-y-0");

        setTimeout(() => {
          dropdownMenu.classList.add("hidden");
          closeMenu.classList.add("hidden");
          openMenu.classList.remove("hidden");
        }, 300);

        document.body.classList.remove("overflow-hidden");
      });
    }

    // --- Nav Link Highlighting ---
    const currentPath = window.location.pathname.replace(/\/$/, "");
    activeLinks.forEach((link) => {
      const linkPath = new URL(
        link.href,
        window.location.origin
      ).pathname.replace(/\/$/, "");
      if (linkPath === currentPath) {
        link.classList.add("active-link");
      }
    });
  },

  initImageUploader: function () {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("event-image");
    const imgView = document.getElementById("img-view");
    const defaultIcon = document.getElementById("default-icon");
    const defaultText = document.getElementById("default-text");
    const defaultSize = document.getElementById("default-size");
    const errorMessage = document.getElementById("image-error");

    if (!dropArea || !fileInput) return;

    // Handle file selection via input
    fileInput.addEventListener("change", (event) => {
      const file = event.target.files[0];
      validateAndPreview(file);
    });

    // Handle drag and drop
    dropArea.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropArea.classList.add("border-cyan-500", "bg-gray-800/30");
    });

    dropArea.addEventListener("dragleave", () => {
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
    });

    dropArea.addEventListener("drop", (event) => {
      event.preventDefault();
      dropArea.classList.remove("border-cyan-500", "bg-gray-800/30");
      const file = event.dataTransfer.files[0];
      if (file) {
        fileInput.files = event.dataTransfer.files;
        validateAndPreview(file);
      }
    });

    // Click handler for the drop area
    dropArea.addEventListener("click", () => {
      fileInput.click();
    });

    function validateAndPreview(file) {
      errorMessage.classList.add("hidden");

      if (!file) return;

      const maxSize = 1_000_000; // 1MB

      if (!file.type.startsWith("image/")) {
        showError("Please select a valid image file");
        resetToDefault();
        return;
      }

      if (file.size > maxSize) {
        showError("File size must be less than 1MB");
        resetToDefault();
        return;
      }

      // Preview the image
      const reader = new FileReader();
      reader.onload = (e) => {
        // Hide default content
        defaultIcon.classList.add("hidden");
        defaultText.classList.add("hidden");
        defaultSize.classList.add("hidden");
        // Set image as background
        imgView.style.backgroundImage = `url(${e.target.result})`;
        imgView.style.backgroundSize = "contain";
        imgView.style.backgroundRepeat = "no-repeat";
        imgView.style.backgroundPosition = "center";
      };
      reader.readAsDataURL(file);
    }

    function showError(message) {
      errorMessage.textContent = message;
      errorMessage.classList.remove("hidden");
      fileInput.value = "";

      // Auto-hide error after 5 seconds
      setTimeout(() => {
        errorMessage.classList.add("hidden");
      }, 5000);
    }

    function resetToDefault() {
      fileInput.value = "";
      defaultIcon.classList.remove("hidden");
      defaultText.classList.remove("hidden");
      defaultSize.classList.remove("hidden");
      imgView.style.backgroundImage = "";
    }
  },

  init: function () {
    this.initTypeaheadSearch();
    this.initFlatpickr();
    this.initImageUploader();
    this.initMobileMenuToggle();
    this.initSearchHighlight();
  },
};

document.addEventListener("DOMContentLoaded", function () {
  setup.init();
});
