/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {LitElement, html, css} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

class SearchEntryPoint extends LitElement {
  static properties = {
    htmlContent: {type: String},
    themeMode: {type: String},
  };

  static styles = css`
    :host {
      display: block;
      margin-top: 16px;
      font-family: 'Google Sans', 'Helvetica Neue', sans-serif;
      /* Apply standard text color from the theme */
      color: var(--md-sys-color-on-surface);
    }

    #container {
      /* Ensure all text inside inherits this color unless specified */
      color: inherit;
    }
    
    /* Example of specific overrides based on theme class */
    #container.dark-theme {
      /* You can add specific dark mode overrides here if needed */
      /* color: #e8eaed; */ 
    }
    
    /* Aggressive Dark Mode Overrides */
    #container.dark-theme * {
      color: var(--md-sys-color-on-surface) !important;
      background: none !important; /* Covers background-color and background-image (gradients) */
      background-color: transparent !important;
      border-color: var(--md-sys-color-outline) !important;
    }

    #container.dark-theme a {
      color: var(--md-sys-color-primary) !important;
    }

    /* Force links to use the primary theme color */
    a {
      color: var(--md-sys-color-primary);
    }
    
    /* Optional: Style generic buttons if they appear in the snippet */
    button {
      background-color: var(--md-sys-color-primary);
      color: var(--md-sys-color-on-primary);
      border: none;
      border-radius: 18px;
      padding: 0 16px;
    }
  `;

  updated(changedProperties) {
    const container = this.shadowRoot.getElementById('container');
    if (!container) return;

    if (changedProperties.has('htmlContent') && this.htmlContent) {
      // The content from search_entry_point is trusted HTML from Google Search
      container.innerHTML = this.htmlContent;
    }

    if (changedProperties.has('themeMode')) {
      if (this.themeMode === 'dark') {
        container.classList.add('dark-theme');
        container.classList.remove('light-theme');
      } else {
        container.classList.add('light-theme');
        container.classList.remove('dark-theme');
      }
    }
  }

  render() {
    return html`<div id="container"></div>`;
  }
}

customElements.define('search-entry-point', SearchEntryPoint);
