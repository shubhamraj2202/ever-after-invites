/**
 * Lantern Animations for Engagement Invitation
 * Creates floating lantern effects in the hero section
 */

class LanternAnimator {
  constructor() {
    this.container = null;
    this.lanterns = [];
    this.config = null;
  }

  /**
   * Initialize lantern animations
   */
  async init() {
    // Wait for config to load
    await this.waitForConfig();

    // Check if lanterns are enabled
    if (!this.config || !this.config.animations.enableLanterns) {
      console.log('Lanterns disabled in config');
      return;
    }

    this.container = document.getElementById('lanterns');
    if (!this.container) {
      console.error('Lanterns container not found');
      return;
    }

    this.createLanterns();
    this.animateLanterns();

    console.log('Lantern animations initialized');
  }

  /**
   * Wait for config to be loaded
   */
  async waitForConfig() {
    return new Promise((resolve) => {
      const checkConfig = () => {
        // Try to get config from global scope or from config file
        if (window.config) {
          this.config = window.config;
          resolve();
        } else {
          // Fetch config directly if not available
          fetch('config.json')
            .then(response => response.json())
            .then(data => {
              this.config = data;
              resolve();
            })
            .catch(() => {
              // Use defaults if config fails to load
              console.warn('Config failed to load, using defaults');
              this.config = {
                animations: {
                  enableLanterns: true,
                  lanternCount: 8
                },
                images: {
                  lanternImage: 'assets/images/lantern-original.png'
                }
              };
              resolve();
            });
        }
      };

      // Check immediately
      checkConfig();
    });
  }

  /**
   * Create lantern elements
   */
  createLanterns() {
    const count = this.config.animations.lanternCount || 8;
    const lanternImage = this.config.images.lanternImage;

    console.log(`Creating ${count} lanterns with image: ${lanternImage}`);

    for (let i = 0; i < count; i++) {
      const lantern = document.createElement('div');
      lantern.className = 'lantern';
      lantern.style.cssText = this.getLanternStyle(i, count);

      // Add image
      const img = document.createElement('img');
      img.src = lanternImage;
      img.alt = 'Floating lantern';
      img.style.cssText = 'width: 100%; height: 100%; object-fit: contain;';

      // Debug: log when image loads
      img.onload = () => console.log(`Lantern ${i} image loaded`);
      img.onerror = () => console.error(`Lantern ${i} image failed to load`);

      lantern.appendChild(img);
      this.container.appendChild(lantern);
      this.lanterns.push(lantern);
    }

    console.log(`${this.lanterns.length} lanterns created and added to container`);
  }

  /**
   * Generate random style for each lantern
   */
  getLanternStyle(index, total) {
    // Distribute lanterns across the viewport
    const left = (index / total) * 100 + (Math.random() * 10 - 5);
    const top = Math.random() * 80; // Keep within viewport
    const size = 60 + Math.random() * 40; // 60-100px
    const delay = Math.random() * 6; // Animation delay
    const duration = 6 + Math.random() * 4; // 6-10s animation duration

    return `
      left: ${left}%;
      top: ${top}%;
      width: ${size}px;
      height: ${size}px;
      animation-delay: ${delay}s;
      animation-duration: ${duration}s;
    `;
  }

  /**
   * Add scroll-based parallax effect to lanterns
   */
  animateLanterns() {
    let ticking = false;

    const updateLanternPositions = () => {
      const scrollY = window.scrollY;
      const heroHeight = document.getElementById('hero').offsetHeight;

      // Only animate when hero section is visible
      if (scrollY < heroHeight) {
        this.lanterns.forEach((lantern, index) => {
          // Different parallax speeds for depth effect
          const speed = 0.3 + (index * 0.05);
          const yOffset = scrollY * speed;

          lantern.style.transform = `translateY(${yOffset}px)`;
        });
      }

      ticking = false;
    };

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(updateLanternPositions);
        ticking = true;
      }
    });

    // Initial position
    updateLanternPositions();
  }

  /**
   * Clean up (if needed)
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
    this.lanterns = [];
  }
}

// Initialize lantern animations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const lanternAnimator = new LanternAnimator();
  lanternAnimator.init();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LanternAnimator;
}
