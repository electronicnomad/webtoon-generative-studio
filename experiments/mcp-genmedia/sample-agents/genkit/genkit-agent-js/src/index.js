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

import { genkit } from "genkit";
import { vertexAI, gemini20Flash } from "@genkit-ai/vertexai";
import { logger } from "genkit/logging";
import { mcpClient } from "genkitx-mcp";

logger.setLogLevel("debug");

const imagenClient = mcpClient({
  name: "imagen",
  version: "1.0.0",
  //serverUrl: "http://localhost:8080/sse",
  serverProcess: {
    command: './mcp-imagen-go',
    env: {"PROJECT_ID": "ghchinoy-genai-sa"},
  },
});

const veoClient = mcpClient({
  name: 'veo',
  version: '1.0.0',
  serverProcess: {
    command: 'mcp-veo-go',
    env: {"PROJECT_ID": "veo-testing"},
  },
});

const chirp3Client = mcpClient({
  name: 'chirp3',
  version: '1.0.0',
  serverProcess: {
    command: 'mcp-chirp3-go',
    env: {"PROJECT_ID": "ghchinoy-genai-sa"},
  },
});

const ai = genkit({
  plugins: [vertexAI({ location: "us-central1" }), 
    imagenClient, 
    veoClient, 
    chirp3Client
  ],
  model: gemini20Flash,
});
