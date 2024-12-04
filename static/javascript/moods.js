// Initialize Swiper
var swiper = new Swiper(".mySwiper", {
  slidesPerView: 1,
  grabCursor: true,
  loop: true,
  pagination: {
      el: ".swiper-pagination",
      clickable: true,
  },
  navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
  },
});

// Select all share buttons in the swiper slides
const shareButtons = document.querySelectorAll('.share-btn');

// Add event listener to each share button
shareButtons.forEach(button => {
  button.addEventListener('click', function() {
      // Get the verse text from the closest slide
      const verseText = this.closest('.slide').querySelector('p').innerText;

      // Check if the browser supports the Web Share API
      if (navigator.share) {
          navigator.share({
              title: 'Bible Verse',
              text: verseText,  // The verse text to share
              url: window.location.href,  // Current page URL
          }).then(() => {
              console.log('Verse shared successfully');
          }).catch((error) => {
              console.log('Error sharing:', error);
          });
      } else {
          // Fallback for browsers that don't support Web Share API
          navigator.clipboard.writeText(verseText).then(() => {
              alert('Verse copied to clipboard!');
          }).catch((error) => {
              console.log('Error copying text:', error);
          });
      }
  });
});
