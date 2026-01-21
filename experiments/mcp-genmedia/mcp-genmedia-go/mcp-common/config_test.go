package common

import (
	"os"
	"testing"
)

func TestLoadConfig(t *testing.T) {
	t.Run("with all env vars set", func(t *testing.T) {
		os.Setenv("PROJECT_ID", "test-project")
		os.Setenv("LOCATION", "test-location")
		os.Setenv("GENMEDIA_BUCKET", "test-bucket")
		
		

		cfg := LoadConfig()

		if cfg.ProjectID != "test-project" {
			t.Errorf("expected ProjectID to be 'test-project', but got '%s'", cfg.ProjectID)
		}
		if cfg.Location != "test-location" {
			t.Errorf("expected Location to be 'test-location', but got '%s'", cfg.Location)
		}
		if cfg.GenmediaBucket != "test-bucket" {
			t.Errorf("expected GenmediaBucket to be 'test-bucket', but got '%s'", cfg.GenmediaBucket)
		}
		
		
	})

	t.Run("with some env vars missing", func(t *testing.T) {
		os.Unsetenv("LOCATION")
		os.Unsetenv("GENMEDIA_BUCKET")
		
		

		cfg := LoadConfig()

		if cfg.Location != "us-central1" {
			t.Errorf("expected Location to be 'us-central1', but got '%s'", cfg.Location)
		}
		if cfg.GenmediaBucket != "" {
			t.Errorf("expected GenmediaBucket to be '', but got '%s'", cfg.GenmediaBucket)
		}
		
		
	})
}
