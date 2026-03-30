console.log("✅ script.js loaded");



document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const menuBtn = document.getElementById("menuBtn");
    const closeBtn = document.getElementById("closeBtn");

    if (!sidebar || !overlay || !menuBtn || !closeBtn) {
        console.error("❌ Sidebar elements missing");
        return;
    }

    menuBtn.onclick = () => {
        sidebar.classList.add("active");
        overlay.classList.add("active");
    };

    closeBtn.onclick = () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    };

    overlay.onclick = () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    };
});


/*-------------------------------------------------------- */
/* START JS FOR AUTOCOMPLETE */

const searchInput = document.querySelector('input[name="search"]');
const suggestionBox = document.getElementById("suggestions");

if (searchInput && suggestionBox) {
    searchInput.addEventListener("input", function () {

        if (this.value.length < 2) {
            suggestionBox.innerHTML = "";
            return;
        }

        fetch(`/search-suggest/?q=${this.value}`)
            .then(res => res.json())
            .then(data => {
                suggestionBox.innerHTML = "";
                data.forEach(item => {
                    suggestionBox.innerHTML += `<div>${item}</div>`;
                });
            });
    });
}
/* -----------------------------------    END JS FOR AUTOCOMPLETE     ----------------------------------------- */

/*=============================================================================
START Left / Right Scroll Logic (Hero Section)
================================================================================*/

let currentSlide = 0;

const slidesWrapper = document.querySelector(".slides");
const slides = document.querySelectorAll(".slide");
const totalSlides = slides.length;

/* 🔐 SAFETY CHECK */
if (slidesWrapper && totalSlides > 0) {

    function updateSlider() {
        slidesWrapper.style.transform =
            `translateX(-${currentSlide * 100}%)`;
    }

    function slideNext() {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateSlider();
    }

    function slidePrev() {
        currentSlide =
            (currentSlide - 1 + totalSlides) % totalSlides;
        updateSlider();
    }

    /* AUTO SLIDE */
    setInterval(slideNext, 5000);
}

/*=================================================================
END Left / Right Scroll Logic (Hero Section)
===================================================================*/


/*=============================================================================
START FINAL AMAZON-STYLE VARIANT SELECTION LOGIC
Auto + Manual (Production Ready)
================================================================================*/
document.addEventListener("DOMContentLoaded", function () {

  const sizeButtons  = document.querySelectorAll(".size-btn");
  const colorButtons = document.querySelectorAll(".color-btn");

  const stockInfo = document.getElementById("stockInfo");

  // CART INPUTS
  const cartSize   = document.getElementById("selectedSize");
  const cartColor  = document.getElementById("selectedColor");
  const cartPrice  = document.getElementById("selectedPrice");
  const cartStock  = document.getElementById("selectedStock");

  // BUY NOW INPUTS
  const buySize    = document.getElementById("buySize");
  const buyColor   = document.getElementById("buyColor");
  const buyPrice   = document.getElementById("buyPrice");
  const buyStock   = document.getElementById("buyStock");


  const addToCartBtn = document.querySelector(".btn.primary");
  const buyNowBtn    = document.querySelector(".btn-buynow");

  let selectedSize  = null;
  let selectedColor = null;

  /* ======================================================
     CASE 1: NO VARIANT PRODUCT
     ====================================================== */
  if (sizeButtons.length === 0 && colorButtons.length === 0) {
    // simple product
    enableButtons();
    if (stockInfo) stockInfo.innerText = "In stock";
    return; // ⛔ no variant logic needed
  }

  /* ======================================================
     INITIAL STATE
     ====================================================== */
  colorButtons.forEach(btn => btn.style.display = "none");
  disableButtons();

  /* ======================================================
     SIZE CLICK LOGIC
     ====================================================== */
  sizeButtons.forEach(btn => {
    btn.addEventListener("click", function () {

      selectedSize = this.dataset.size;
      if (cartSize) cartSize.value = selectedSize;
      if (buySize)  buySize.value  = selectedSize;


      // UI active
      sizeButtons.forEach(b => b.classList.remove("active"));
      this.classList.add("active");

      // reset color
      selectedColor = null;

      if (cartColor) cartColor.value = "";
      if (buyColor)  buyColor.value  = "";

      if (cartStock) cartStock.value = "";
      if (buyStock)  buyStock.value  = "";


      colorButtons.forEach(c => {
        c.classList.remove("active");
        c.style.display = "none";
      });

      // show colors for this size
      const matchingColors = [];
      colorButtons.forEach(c => {
        if (c.dataset.size === selectedSize) {
          c.style.display = "inline-block";
          matchingColors.push(c);
        }
      });

      stockInfo.innerText = "Select color";
      disableButtons();

      /* ==================================================
         AUTO SELECT COLOR (ONLY IF ONE OPTION)
         ================================================== */
      if (matchingColors.length === 1) {
        matchingColors[0].click();
        stockInfo.innerText = " Select Color";
      }
    });
  });

  /* ======================================================
     COLOR CLICK LOGIC
     ====================================================== */
  colorButtons.forEach(btn => {
    btn.addEventListener("click", function () {

      if (!selectedSize) {
        showMessage("Please select size first");
        return;
      }

      selectedColor = this.dataset.color;
      const stock = parseInt(this.dataset.stock || 0);
      const price = this.dataset.price || null;

      // ✅ SAFE ASSIGNMENT (YAHI ADD KARNA THA)
      // CART
      if (cartColor) cartColor.value = selectedColor;
      if (cartPrice && price) cartPrice.value = price;
      if (cartStock) cartStock.value = stock;

      // BUY NOW
      if (buyColor) buyColor.value = selectedColor;
      if (buyStock) buyStock.value = stock;
      if (buyPrice && price) buyPrice.value = price;

      // 🔥 UPDATE VISIBLE PRICE
      const priceElement = document.getElementById("productPrice");
      if (priceElement && price) {
          priceElement.innerText = price;
      }



      colorButtons.forEach(b => b.classList.remove("active"));
      this.classList.add("active");

      if (stock > 0) {
        stockInfo.innerText = `Only ${stock} left in stock`;
        enableButtons();
      } else {
        stockInfo.innerText = "Out of stock";
        disableButtons();
      }
    });
  });

  /* ======================================================
     CASE 2: SINGLE VARIANT PRODUCT (AUTO)
     ====================================================== */
  if (sizeButtons.length === 1) {
    sizeButtons[0].click();
    stockInfo.innerText = "Select size & color ";
  }

  /* ======================================================
     BUTTON PROTECTION (NO FORCE, JUST SAFETY)
     ====================================================== */
  [addToCartBtn, buyNowBtn].forEach(btn => {
    if (!btn) return;

    btn.addEventListener("click", function (e) {
      if (!selectedSize || !selectedColor) {
        e.preventDefault();
        showMessage("⚠ Please select size & color");
      }
    });
  });

  /* ======================================================
     HELPERS
     ====================================================== */
  function disableButtons() {
    [addToCartBtn, buyNowBtn].forEach(btn => {
      if (!btn) return;
      btn.style.pointerEvents = "none";
      btn.style.opacity = "0.5";
    });
  }

  function enableButtons() {
    [addToCartBtn, buyNowBtn].forEach(btn => {
      if (!btn) return;
      btn.style.pointerEvents = "auto";
      btn.style.opacity = "1";
    });
  }

  function showMessage(msg) {
    stockInfo.innerText = msg;
    stockInfo.style.color = "#dc2626";
    setTimeout(() => stockInfo.style.color = "", 2000);
  }

});


/*=============================================================================
END FINAL VARIANT SELECTION LOGIC
================================================================================*/

/*=============================================================================
START Thumbnail click → main image change
================================================================================*/
function changeMainImage(thumbnail) {
  const mainImage = document.getElementById("mainProductImage");
  mainImage.src = thumbnail.src;

  // active thumbnail highlight
  document.querySelectorAll(".thumbnail").forEach(img => {
    img.classList.remove("active");
  });
  thumbnail.classList.add("active");
}
/*=============================================================================
END Thumbnail click → main image change
================================================================================*/



/*=============================================================================
START JS FOR Even Better UX – Zoom Follow Cursor
================================================================================*/

const zoomContainer = document.querySelector(".image-zoom-container");
const zoomImage = document.querySelector(".main-image");

if (zoomContainer && zoomImage) {
  zoomContainer.addEventListener("mousemove", (e) => {
    const rect = zoomContainer.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    zoomImage.style.transformOrigin = `${x}% ${y}%`;
  });

  zoomContainer.addEventListener("mouseleave", () => {
    zoomImage.style.transformOrigin = "center center";
  });
}

/*==============================================================================
END JS FOR Even Better UX – Zoom Follow Cursor
================================================================================*/
