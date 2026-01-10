/**
 * Configuration Loader for Engagement Invitation
 * Loads config.json and populates the page dynamically
 */

class ConfigLoader {
  constructor() {
    this.config = null;
  }

  /**
   * Load configuration from JSON file
   */
  async load(configPath = 'config.json') {
    try {
      const response = await fetch(configPath);
      if (!response.ok) {
        throw new Error(`Failed to load config: ${response.statusText}`);
      }
      this.config = await response.json();
      console.log('Config loaded successfully:', this.config);
      return this.config;
    } catch (error) {
      console.error('Error loading config:', error);
      throw error;
    }
  }

  /**
   * Get nested value from config using dot notation
   * e.g., "couple.name1" returns config.couple.name1
   */
  getNestedValue(path) {
    return path.split('.').reduce((obj, key) => obj?.[key], this.config);
  }

  /**
   * Populate page content using data-config attributes
   */
  applyContent() {
    if (!this.config) {
      console.error('Config not loaded');
      return;
    }

    // Find all elements with data-config attributes
    document.querySelectorAll('[data-config]').forEach(element => {
      const path = element.getAttribute('data-config');
      const value = this.getNestedValue(path);

      if (value !== undefined && value !== null) {
        // Handle different element types
        if (element.tagName === 'IMG') {
          element.src = value;
          element.alt = path;
        } else if (element.tagName === 'A') {
          // For links, set href
          if (element.hasAttribute('data-config-href')) {
            element.href = value;
          } else {
            element.textContent = value;
          }
        } else if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
          element.value = value;
        } else {
          // For regular elements, set text content
          element.textContent = value;
        }
      }
    });

    // Special handling for WhatsApp RSVP link
    const rsvpButton = document.querySelector('[data-rsvp-whatsapp]');
    if (rsvpButton && this.config.content.rsvpWhatsApp) {
      const phoneNumber = this.config.content.rsvpWhatsApp.replace(/[^0-9]/g, '');
      const message = encodeURIComponent(this.config.content.rsvpWhatsAppMessage);
      rsvpButton.href = `https://wa.me/${phoneNumber}?text=${message}`;
    }

    // Special handling for Google Maps link
    const mapsButton = document.querySelector('[data-maps-link]');
    if (mapsButton && this.config.event.venue.googleMapsLink) {
      mapsButton.href = this.config.event.venue.googleMapsLink;
    }

    // Populate gallery images
    this.populateGallery();

    // Populate things to know
    this.populateThingsToKnow();
  }

  /**
   * Apply color scheme from config
   */
  applyTheme() {
    if (!this.config || !this.config.styling) {
      console.error('Styling config not found');
      return;
    }

    const root = document.documentElement;
    const colors = this.config.styling.colorScheme;

    // Apply CSS custom properties
    root.style.setProperty('--primary-color', colors.primary);
    root.style.setProperty('--secondary-color', colors.secondary);
    root.style.setProperty('--accent-color', colors.accent);
    root.style.setProperty('--text-color', colors.text);
    root.style.setProperty('--text-light-color', colors.textLight);
    root.style.setProperty('--background-color', colors.background);
    root.style.setProperty('--background-alt-color', colors.backgroundAlt);

    // Apply fonts
    if (this.config.styling.fonts) {
      root.style.setProperty('--font-heading', this.config.styling.fonts.heading);
      root.style.setProperty('--font-body', this.config.styling.fonts.body);
    }

    // Apply hero background image from config
    if (this.config.images && this.config.images.heroImage) {
      const heroSection = document.getElementById('hero');
      if (heroSection) {
        heroSection.style.backgroundImage = `url('${this.config.images.heroImage}')`;
        console.log('Hero background image applied:', this.config.images.heroImage);
      }
    }

    console.log('Theme applied successfully');
  }

  /**
   * Populate gallery images
   */
  populateGallery() {
    const galleryContainer = document.querySelector('[data-gallery]');
    if (!galleryContainer || !this.config.images.galleryImages) {
      return;
    }

    // Clear existing content
    galleryContainer.innerHTML = '';

    // Add images from config
    this.config.images.galleryImages.forEach((imagePath, index) => {
      const imgElement = document.createElement('div');
      imgElement.className = 'gallery-item fade-in';
      imgElement.innerHTML = `
        <img src="${imagePath}" alt="Gallery image ${index + 1}" loading="lazy">
      `;
      galleryContainer.appendChild(imgElement);
    });
  }

  /**
   * Populate things to know section
   */
  populateThingsToKnow() {
    const container = document.querySelector('[data-things-to-know]');
    if (!container || !this.config.thingsToKnow) {
      return;
    }

    // Clear existing content
    container.innerHTML = '';

    // Add items from config
    this.config.thingsToKnow.items.forEach(item => {
      const itemElement = document.createElement('div');
      itemElement.className = 'info-item fade-in';
      itemElement.innerHTML = `
        <div class="info-icon">${item.icon}</div>
        <div class="info-content">
          <h4>${item.label}</h4>
          <p>${item.value}</p>
        </div>
      `;
      container.appendChild(itemElement);
    });
  }

  /**
   * Initialize all config-driven features
   */
  async init() {
    try {
      await this.load();
      this.applyTheme();
      this.applyContent();

      // Initialize animations if enabled
      if (this.config.animations.enableScrollAnimations) {
        this.initScrollAnimations();
      }

      console.log('Config loader initialized successfully');
    } catch (error) {
      console.error('Failed to initialize config loader:', error);
    }
  }

  /**
   * Initialize scroll-based fade-in animations
   */
  initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    // Observe all fade-in elements
    document.querySelectorAll('.fade-in').forEach(element => {
      observer.observe(element);
    });
  }
}

// Initialize config loader when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  const configLoader = new ConfigLoader();
  await configLoader.init();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ConfigLoader;
}
