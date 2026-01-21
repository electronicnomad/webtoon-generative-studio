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

import { LitElement, css, html } from "https://cdn.jsdelivr.net/npm/lit/+esm";
import { SvgIcon } from "../svg_icon/svg_icon.js";

class CopyButton extends LitElement {
  static styles = css`
    .copy-button {
      cursor: pointer;
      padding: 4px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.2s ease-in-out;
    }
    .copy-button:hover {
      background-color: var(--mesop-surface-container-hover-color);
    }
    svg-icon {
      width: 20px;
      height: 20px;
      color: var(--mesop-on-surface-variant-color);
    }
  `;

  static get properties() {
    return {
      textToCopy: { type: String },
      _copied: { state: true },
    };
  }

  constructor() {
    super();
    this.textToCopy = "";
    this._copied = false;
  }

  handleClick() {
    if (!navigator.clipboard) {
      console.warn("Copy to clipboard is not supported in this browser.");
      return;
    }
    navigator.clipboard.writeText(this.textToCopy).then(() => {
      this._copied = true;
      setTimeout(() => {
        this._copied = false;
      }, 2000); // Revert back after 2 seconds
    });
  }

  render() {
    return html`
      <div class="copy-button" @click=${this.handleClick}>
        <svg-icon .iconName=${this._copied ? "task_alt" : "content_copy"}></svg-icon>
      </div>
    `;
  }
}

customElements.define("copy-button", CopyButton);
