package main

import (
	"context"
	"testing"
)

func TestRunFFmpegCommand(t *testing.T) {
	// This is a basic test to ensure that the command is executed without errors.
	// It doesn't validate the output of the command.
	_, err := runFFmpegCommand(context.Background(), "-version")
	if err != nil {
		t.Errorf("expected no error, but got: %v", err)
	}
}
