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
import 'https://cdn.jsdelivr.net/npm/@material/mwc-button/+esm';

class SelfieCamera extends LitElement {
  static styles = css`
    :host {
      display: block;
      border: 1px solid var(--mesop-outline-variant-color);
      border-radius: 12px;
      overflow: hidden;
      position: relative;
      width: 400px;
      height: 300px;
    }
    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .controls {
      position: absolute;
      bottom: 10px;
      left: 50%;
      transform: translateX(-50%);
    }
  `;

  static get properties() {
    return {
      capture: { type: String },
    };
  }

  constructor() {
    super();
    this.capture = "";
    this.stream = null;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      console.log("Camera stream stopped.");
    }
  }

  firstUpdated() {
    this.videoElement = this.shadowRoot.querySelector("video");
    this.canvasElement = this.shadowRoot.querySelector("canvas");
    this.startCamera();
  }

  async startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoElement.srcObject = stream;
      this.stream = stream; // Store the stream for cleanup
    } catch (err) {
      console.error("Error accessing camera:", err);
    }
  }

  takePicture() {
    console.log("Taking picture...");
    const video = this.videoElement;
    const canvas = this.canvasElement;
    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/png");

    if (this.capture) {
      console.log("Dispatching capture event...");
      this.dispatchEvent(new MesopEvent(this.capture, { value: dataUrl }));
    } else {
      console.error("Capture event handler not set.");
    }
  }

  render() {
    return html`
      <video autoplay playsinline></video>
      <canvas style="display:none;"></canvas>
      <div class="controls">
        <mwc-button raised label="Take Picture" @click=${this.takePicture}></mwc-button>
      </div>
    `;
  }
}

customElements.define("selfie-camera", SelfieCamera);