import { LitElement, css, html } from "https://cdn.jsdelivr.net/npm/lit/+esm";

class ScrollSentinel extends LitElement {
  static styles = css`
    :host {
      display: block;
      width: 100%;
      height: 100px; /* Give it some space to be observed */
      display: flex;
      justify-content: center;
      align-items: center;
    }
  `;

  static get properties() {
    return {
      isLoading: { type: Boolean },
      allItemsLoaded: { type: Boolean },
      visible: { type: String }, // Event handler ID
    };
  }

  constructor() {
    super();
    this.isLoading = false;
    this.allItemsLoaded = false;
    this.visible = "";
    this.observer = null;
    this.debounceTimeout = null;
  }

  connectedCallback() {
    super.connectedCallback();
    this.observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        if (!this.isLoading && !this.allItemsLoaded && this.visible) {
          // Clear any pending timeout to avoid multiple dispatches
          if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
          }
          // Set a short timeout to debounce the event
          this.debounceTimeout = setTimeout(() => {
            this.dispatchEvent(new MesopEvent(this.visible, {}));
          }, 50); // 50ms debounce window
        }
      } else {
        // If it's not intersecting, clear any pending event dispatch
        if (this.debounceTimeout) {
          clearTimeout(this.debounceTimeout);
        }
      }
    });
    this.observer.observe(this);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.observer) {
      this.observer.disconnect();
    }
    // Also clear any pending timeout to prevent the event from firing after disconnect
    if (this.debounceTimeout) {
      clearTimeout(this.debounceTimeout);
    }
  }

  render() {
    if (this.isLoading) {
      return html`<p>Loading...</p>`;
    }
    if (this.allItemsLoaded) {
      return html`<p>End of list</p>`;
    }
    return html``; // Otherwise, be invisible
  }
}

customElements.define("scroll-sentinel", ScrollSentinel);
