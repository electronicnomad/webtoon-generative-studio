#!/bin/bash
#
# This script performs a basic verification of the mcp-imagen-go server.
# It ensures that the server builds and is responsive to a basic MCP request.

set -e

echo "Building mcp-imagen-go..."
go build

echo "Verifying mcp-imagen-go server..."
mcptools tools ./mcp-imagen-go

echo "Verification successful!"
